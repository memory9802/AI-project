let selectedTags = [];
let currentOutfitId = null;
let selectedRating = 0;
// track comment rating changes (commentId -> rating)
const changedCommentRatings = new Map();

// ===== Tag Selection =====
document.querySelectorAll('.tag-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const tag = btn.dataset.tag;
    if (selectedTags.includes(tag)) {
      selectedTags = selectedTags.filter(t => t !== tag);
      btn.classList.remove('bg-primary/30', 'text-primary');
    } else {
      selectedTags.push(tag);
      btn.classList.add('bg-primary/30', 'text-primary');
    }
    updateSelectedTags();
  });
});

function updateSelectedTags() {
  const container = document.getElementById('selected-tags');
  container.innerHTML = selectedTags.map(tag =>
    `<span class="px-3 py-1 rounded-full text-sm bg-primary/20 text-primary">${tag}</span>`
  ).join('');
  document.getElementById('tags-input').value = selectedTags.join(',');
}

// ===== Image Upload =====
const uploadArea = document.getElementById('upload-area');
const imageInput = document.getElementById('image-input');
const previewImage = document.getElementById('preview-image');

uploadArea.addEventListener('click', () => imageInput.click());

uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('bg-primary/10');
});

uploadArea.addEventListener('dragleave', () => {
  uploadArea.classList.remove('bg-primary/10');
});

uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('bg-primary/10');
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    imageInput.files = files;
    displayPreview();
  }
});

imageInput.addEventListener('change', displayPreview);

function displayPreview() {
  const file = imageInput.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImage.src = e.target.result;
      previewImage.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  }
}

// ===== Modal Star Rating (moved from Add Comment area) =====
const modalStars = document.querySelectorAll('#modal-rating .star');
const modalRatingValue = document.getElementById('modal-rating-value');
const modalRatingSubmit = document.getElementById('modal-rating-submit');
const modalRatingContainer = document.getElementById('modal-rating');

if (modalRatingContainer && modalStars.length > 0 && modalRatingValue) {
  modalStars.forEach(star => {
    star.addEventListener('click', async () => {
      selectedRating = parseInt(star.dataset.rating);
      modalRatingValue.value = selectedRating;
      modalStars.forEach((s, idx) => {
        if (idx < selectedRating) {
          s.classList.add('active');
        } else {
          s.classList.remove('active');
        }
      });
    });

    star.addEventListener('mouseover', () => {
      modalStars.forEach((s, idx) => {
        if (idx < star.dataset.rating) {
          s.style.color = '#D8A7B1';
        } else {
          s.style.color = '#888888';
        }
      });
    });
  });
} else {
  // Modal rating header controls removed; preserve variables but don't add listeners
}


// reset overlay when leaving
const modalRatingContainerCheck = document.getElementById('modal-rating');
if (modalRatingContainerCheck) {
  modalRatingContainerCheck.addEventListener('mouseout', () => {
    modalStars.forEach((s, idx) => {
      if (idx < selectedRating) {
        s.classList.add('active');
      } else {
        s.classList.remove('active');
      }
    });
  });
}

// submit rating for current outfit (header-level modal rating removed — only attach listener if present)
if (modalRatingSubmit) {
  modalRatingSubmit.addEventListener('click', async (e) => {
    e.preventDefault();
    if (!currentOutfitId) {
      alert('無法評分，請先選擇穿搭');
      return;
    }
    if (!selectedRating || selectedRating <= 0) {
      alert('請選擇評分星數');
      return;
    }

    try {
      const res = await fetch(`/share/api/outfits/${currentOutfitId}/rate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating: parseInt(selectedRating) })
      });
      if (res.ok) {
        alert('評分已提交！');
        modal.classList.add('hidden');
        loadOutfits();
      } else {
        alert('評分提交失敗');
      }
    } catch (err) {
      alert('錯誤: ' + err.message);
    }
  });
}



// ===== Modal Controls =====
const modal = document.getElementById('comments-modal');
const closeBtn = document.getElementById('close-modal');

closeBtn.addEventListener('click', () => {
  modal.classList.add('hidden');
});

modal.addEventListener('click', (e) => {
  if (e.target === modal) {
    modal.classList.add('hidden');
  }
});

// Helper to render stars for displays. Can be interactive for comments
function renderStars(rating, size = 'small', interactive = false) {
  const r = parseInt(rating) || 0;
  let output = '';
  for (let i = 1; i <= 5; i++) {
    if (interactive) {
      output += `<span class="star ${size} comment-star ${i <= r ? 'filled' : 'empty'}" data-rating="${i}">★</span>`;
    } else {
      output += `<span class="star ${size} ${i <= r ? 'filled' : 'empty'}" data-rating="${i}">★</span>`;
    }
  }
  return output;
} 

// ===== Upload Form =====
document.getElementById('upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const file = imageInput.files[0];
  const description = document.getElementById('description-input').value;

  if (!file || !description) {
    alert('請上傳照片並填寫描述');
    return;
  }

  const formData = new FormData();
  formData.append('image', file);
  formData.append('description', description);
  formData.append('tags', selectedTags.join(','));

  try {
    const res = await fetch('/share/api/outfits', {
      method: 'POST',
      body: formData
    });

    if (res.ok) {
      alert('穿搭已上傳！');
      document.getElementById('upload-form').reset();
      previewImage.classList.add('hidden');
      selectedTags = [];
      document.querySelectorAll('.tag-btn').forEach(btn => {
        btn.classList.remove('bg-primary/30', 'text-primary');
      });
      updateSelectedTags();
      loadOutfits();
    } else {
      alert('上傳失敗');
    }
  } catch (err) {
    alert('錯誤: ' + err.message);
  }
});

// ===== Load Outfits =====
async function loadOutfits() {
  try {
    const res = await fetch('/share/api/outfits');
    const outfits = await res.json();

    const container = document.getElementById('outfits-container');
    container.innerHTML = outfits.map(outfit => `
    <div class="bg-white dark:bg-secondary-dark rounded-lg overflow-hidden shadow-sm border border-secondary-light dark:border-secondary-dark">
      <!-- Outfit Image -->
      <img src="${outfit.image_url}" alt="outfit" class="w-full h-64 object-cover" />

      <!-- Outfit Info -->
            <div class="p-6">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="text-lg font-bold">${outfit.user_name || '匿名用戶'}</h3>
            <p class="text-sm text-subtle-light dark:text-subtle-dark">${new Date(outfit.created_at).toLocaleDateString('zh-TW')}</p>
          </div>
          <div class="text-right">
            <div class="flex items-center gap-1 mb-1">
              <span class="material-symbols-outlined text-lg text-primary">star</span>
              <span class="font-bold">${outfit.avg_rating ? outfit.avg_rating.toFixed(1) : '0.0'}</span>
            </div>
            <p class="text-xs text-subtle-light dark:text-subtle-dark">${outfit.comment_count || 0} 評論</p>
          </div>
        </div>

        <p class="text-sm mb-4 text-text-light dark:text-text-dark">${outfit.description}</p>

        <!-- Tags -->
        ${outfit.tags ? `
          <div class="flex flex-wrap gap-2 mb-4">
            ${outfit.tags.split(',').map(tag =>
      `<span class="px-3 py-1 rounded-full text-xs bg-primary/10 text-primary">${tag}</span>`
    ).join('')}
          </div>
        ` : ''}

        <!-- Weight info (hidden by default, useful for debugging/dev) -->
        <div class="weight-info hidden text-xs text-subtle-light mt-2">評分權重: ${outfit.rating_weight || '—'} 人氣權重: ${outfit.popularity_weight || '—'} 綜合分數: ${outfit.final_score || '—'}</div>

        <!-- Actions: only rating button available -->
        <div class="flex gap-3 pt-4 border-t border-secondary-light dark:border-secondary-dark">
          <div class="w-full">
            ${outfit.user_rating ? `
              <button class="rate-btn rated w-full px-4 py-3 rounded-lg bg-gray-200 text-subtle-light" disabled>已評分 ★ ${outfit.user_rating}</button>
            ` : `
              <button class="rate-btn rate-open w-full px-4 py-3 rounded-lg bg-primary text-white" data-outfit-id="${outfit.id}">評分此穿搭</button>
            `}
          </div>
        </div>
      </div>
    </div>
  `).join('');

    // Add event listeners for rate button that opens modal

    // Rate button handlers: open comments modal (also contains rating)
    document.querySelectorAll('.rate-btn.rate-open').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const outfitId = btn.dataset.outfitId;
        currentOutfitId = outfitId;
        await loadComments(outfitId);
        modal.classList.remove('hidden');
      });
    });
  } catch (err) {
    console.error('Error loading outfits:', err);
  }
}

// ===== Load Comments =====
async function loadComments(outfitId) {
  try {
    changedCommentRatings.clear();
    const res = await fetch(`/share/api/outfits/${outfitId}/comments`);
    const comments = await res.json();

    const content = document.getElementById('comments-content');
    content.innerHTML = comments.map(comment => `
    <div class="mb-4 pb-4 border-b border-secondary-light dark:border-secondary-dark last:border-b-0">
      <div class="flex items-start justify-between mb-2">
        <div class="flex items-center gap-3">
          ${comment.img_url ? `<img src="${comment.img_url}" alt="comment image" class="h-10 w-10 rounded-md object-cover">` : `<div class="h-10 w-10 rounded-md bg-secondary-light dark:bg-secondary-dark"></div>`}
          <div>
            <p class="text-xs text-subtle-light dark:text-subtle-dark">${new Date(comment.created_at).toLocaleDateString('zh-TW')}</p>
          </div>
        </div>
        <div class="comment-rating flex items-center gap-1" data-comment-id="${comment.id}" data-comment-rating="${comment.rating}" data-outfit-id="${outfitId}">
          ${renderStars(0, 'small', true)}
        </div>
      </div>
    </div>
  `).join('');

    selectedRating = 0;
    if (modalRatingValue) modalRatingValue.value = 0;
    if (modalStars && modalStars.length) modalStars.forEach(s => s.classList.remove('active'));

    // Attach interactive listeners for comment stars
    attachCommentStarListeners();

  } catch (err) {
    console.error('Error loading comments:', err);
  }
}

// Attach interactive listeners to comment stars
function attachCommentStarListeners() {
  document.querySelectorAll('.comment-rating').forEach(container => {
    const commentId = container.dataset.commentId;
    const outfitId = container.dataset.outfitId || currentOutfitId;
    const initialRating = parseInt(container.dataset.commentRating) || 0; // backend rating
    const stars = container.querySelectorAll('.comment-star');

    // helper to set visual state according to rating
    const setVisual = (rating) => {
      stars.forEach((s, idx) => {
        if (idx < rating) {
          s.classList.add('filled');
          s.classList.remove('empty');
        } else {
          s.classList.remove('filled');
          s.classList.add('empty');
        }
      });
      // keep backend rating separate; do not overwrite dataset.commentRating
    };

    // initialize visual state to 0 (user must click to set rating)
    setVisual(0);
    container.dataset.userRating = 0;

    // hover behavior
    stars.forEach(s => {
      s.addEventListener('mouseover', () => {
        const r = parseInt(s.dataset.rating);
        setVisual(r);
      });

      s.addEventListener('mouseout', () => {
        const userRating = parseInt(container.dataset.userRating) || 0;
        setVisual(userRating);
      });

      s.addEventListener('click', (e) => {
        const r = parseInt(s.dataset.rating);
        // locally update visual and record user selection
        setVisual(r);
        container.dataset.userRating = r;
        changedCommentRatings.set(commentId, r);
      });
    });
  });
}



// ===== Initial Load =====

// submit changed comment ratings
const submitCommentRatingsBtn = document.getElementById('submit-comment-ratings');
if (submitCommentRatingsBtn) {
  submitCommentRatingsBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    if (!currentOutfitId) {
      alert('無法提交評分，請先選擇穿搭');
      return;
    }
    if (changedCommentRatings.size === 0) {
      alert('沒有要提交的評論評分');
      return;
    }

    try {
      // send all changed ratings in parallel
      const requests = [];
      for (const [commentId, rating] of changedCommentRatings.entries()) {
        requests.push(fetch(`/share/api/outfits/${currentOutfitId}/comments/${commentId}/rate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ rating: rating })
        }));
      }

      const results = await Promise.all(requests);
      if (results.every(r => r.ok)) {
        alert('評論評分已提交！');
        changedCommentRatings.clear();
        await loadComments(currentOutfitId);
      } else {
        alert('部分評分提交失敗');
      }
    } catch (err) {
      alert('錯誤: ' + err.message);
    }
  });
}

loadOutfits();