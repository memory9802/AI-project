import os
import time
import uuid
from datetime import datetime

from flask import current_app, g, jsonify, render_template, request, url_for
from werkzeug.utils import secure_filename

from database import get_db_cursor
from auth import login_required, get_current_user
from . import wardrobe_bp

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _serialize_item(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "item_name": row.get("item_name"),
        "category": row.get("category"),
        "color": row.get("color"),
        "tags": row.get("tags"),
        "image_url": row.get("image_url"),
        "uploaded_at": row.get("uploaded_at").isoformat() if row.get("uploaded_at") else None,
    }


@wardrobe_bp.route('/wardrobe')
@login_required
def wardrobe():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('wardrobe.html', user=user)


@wardrobe_bp.route('/deals')
@login_required
def deals():
    user = getattr(g, 'current_user', get_current_user())
    return render_template('deals.html', user=user)


@wardrobe_bp.route('/items', methods=['GET'])
@login_required
def list_items():
    """Return wardrobe items for the logged-in user."""
    user = getattr(g, 'current_user', get_current_user())
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, item_name, category, color, tags, image_url, uploaded_at
            FROM user_wardrobe
            WHERE user_id = %s
            ORDER BY uploaded_at DESC
            """,
            (user['id'],),
        )
        rows = cursor.fetchall() or []

    return jsonify({
        "success": True,
        "user": user,
        "items": [_serialize_item(row) for row in rows],
    })


@wardrobe_bp.route('/items', methods=['POST'])
@login_required
def add_item():
    """Upload wardrobe items (supports multiple images) for the logged-in user."""
    user = getattr(g, 'current_user', get_current_user())
    item_name = (request.form.get('item_name') or "").strip()
    category = (request.form.get('category') or "").strip()
    color = (request.form.get('color') or "").strip()
    tags_raw = (request.form.get('tags') or "").strip()

    selected_tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    images = request.files.getlist('images') or request.files.getlist('image')

    if not item_name or not category or not color:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if not selected_tags:
        return jsonify({"success": False, "message": "Select at least one style tag."}), 400
    if not images:
        return jsonify({"success": False, "message": "Upload at least one image."}), 400

    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'wardrobe')
    os.makedirs(upload_dir, exist_ok=True)

    saved_items = []
    with get_db_cursor() as cursor:
        for image in images:
            if not image or not image.filename:
                continue
            if not _allowed_file(image.filename):
                return jsonify({"success": False, "message": "Only image files are allowed (png, jpg, jpeg, gif, webp)."}), 400

            _, ext = os.path.splitext(secure_filename(image.filename))
            unique_name = f"user{user['id']}_{int(time.time())}_{uuid.uuid4().hex[:8]}{ext.lower()}"
            save_path = os.path.join(upload_dir, unique_name)
            image.save(save_path)

            image_url = url_for('static', filename=f"uploads/wardrobe/{unique_name}")
            cursor.execute(
                """
                INSERT INTO user_wardrobe (user_id, item_name, category, color, tags, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user['id'],
                    item_name,
                    category,
                    color,
                    ",".join(selected_tags),
                    image_url,
                ),
            )
            saved_items.append({
                "id": cursor.lastrowid,
                "item_name": item_name,
                "category": category,
                "color": color,
                "tags": ",".join(selected_tags),
                "image_url": image_url,
                "uploaded_at": datetime.utcnow().isoformat(),
            })

    return jsonify({
        "success": True,
        "message": "Item saved to wardrobe.",
        "items": saved_items,
        "user": user,
    }), 201


@wardrobe_bp.route('/items/delete', methods=['POST'])
@login_required
def delete_items():
    """Delete selected wardrobe items for the logged-in user."""
    user = getattr(g, 'current_user', get_current_user())
    payload = request.get_json(silent=True) or {}
    raw_ids = payload.get("ids") or []

    try:
        item_ids = [int(i) for i in raw_ids if str(i).strip().isdigit()]
    except Exception:
        return jsonify({"success": False, "message": "Invalid item ids."}), 400

    if not item_ids:
        return jsonify({"success": False, "message": "No items selected."}), 400

    placeholders = ",".join(["%s"] * len(item_ids))
    deleted = []
    image_paths = []

    with get_db_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT id, image_url
            FROM user_wardrobe
            WHERE user_id = %s AND id IN ({placeholders})
            """,
            (user['id'], *item_ids),
        )
        rows = cursor.fetchall() or []
        if not rows:
            return jsonify({"success": False, "message": "No matching items found."}), 404

        cursor.execute(
            f"DELETE FROM user_wardrobe WHERE user_id = %s AND id IN ({placeholders})",
            (user['id'], *item_ids),
        )
        deleted = [row["id"] for row in rows]
        for row in rows:
            image_url = row.get("image_url") or ""
            static_prefix = current_app.static_url_path.rstrip("/") + "/"
            if image_url.startswith(static_prefix):
                rel_path = image_url[len(static_prefix):]
            elif image_url.startswith("/static/"):
                rel_path = image_url[len("/static/"):]
            else:
                rel_path = None

            if rel_path:
                image_paths.append(os.path.join(current_app.static_folder, rel_path))

    for path in image_paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass

    return jsonify({
        "success": True,
        "deleted_ids": deleted,
        "message": f"Deleted {len(deleted)} item(s).",
    }), 200
