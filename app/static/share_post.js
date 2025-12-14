let selectedTags = [];
let currentOutfitId = null;
let selectedRating = 0;
// track comment rating changes (commentId -> rating)
const changedCommentRatings = new Map();

// ===== Upload Modal Controls =====
const uploadModal = document.getElementById('upload-modal');
const openUploadBtn = document.getElementById('open-upload-modal');
const closeUploadBtn = document.getElementById('close-upload-modal');

if (openUploadBtn) {
  openUploadBtn.addEventListener('click', () => {
    uploadModal.classList.remove('hidden');
  });
}

if (closeUploadBtn) {
  closeUploadBtn.addEventListener('click', () => {
    uploadModal.classList.add('hidden');
  });
}

// Close upload modal when clicking outside
uploadModal.addEventListener('click', (e) => {
  if (e.target === uploadModal) {
    uploadModal.classList.add('hidden');
  }
});

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

        <!-- Actions: two separate buttons -->
        <div class="flex gap-3 pt-4 border-t border-secondary-light dark:border-secondary-dark">
          <button class="rate-comment-btn flex-1 px-4 py-3 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors" data-outfit-id="${outfit.id}">
            <span class="material-symbols-outlined inline-block align-middle text-lg">rate_review</span>
            <span class="align-middle">評論與評分</span>
          </button>
          <button class="view-items-btn flex-1 px-4 py-3 rounded-lg bg-secondary-light dark:bg-secondary-dark text-text-light dark:text-text-dark hover:bg-primary/20 dark:hover:bg-primary/30 transition-colors" data-outfit-id="${outfit.id}">
            <span class="material-symbols-outlined inline-block align-middle text-lg">checkroom</span>
            <span class="align-middle">查看單品</span>
          </button>
        </div>
      </div>
    </div>
  `).join('');

    // Add event listeners for buttons that open modal

    // 評論與評分按鈕：顯示總體評分 + 評論區塊
    document.querySelectorAll('.rate-comment-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const outfitId = btn.dataset.outfitId;
        currentOutfitId = outfitId;
        
        // 找到對應的 outfit 資料
        const outfit = outfits.find(o => o.id == outfitId);
        
        await loadComments(outfitId, outfit, 'comment');
        modal.classList.remove('hidden');
      });
    });
    
    // 查看單品按鈕：顯示單品評分
    document.querySelectorAll('.view-items-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const outfitId = btn.dataset.outfitId;
        currentOutfitId = outfitId;
        
        // 找到對應的 outfit 資料
        const outfit = outfits.find(o => o.id == outfitId);
        
        await loadComments(outfitId, outfit, 'items');
        modal.classList.remove('hidden');
      });
    });
  } catch (err) {
    console.error('Error loading outfits:', err);
  }
}

// Note: Overall rating section now displays read-only info (image + current rating)

// ===== Load Comments =====
async function loadComments(outfitId, outfit, mode = 'comment') {
  try {
    changedCommentRatings.clear();
    
    // 根據模式顯示/隱藏不同區域
    const overallRatingSection = document.getElementById('overall-rating-section');
    const commentsSection = document.getElementById('comments-section-wrapper');
    const itemsSection = document.getElementById('items-section');
    
    if (mode === 'comment') {
      // 評論與評分模式：顯示總體評分 + 評論
      if (overallRatingSection) overallRatingSection.classList.remove('hidden');
      if (commentsSection) commentsSection.classList.remove('hidden');
      if (itemsSection) itemsSection.classList.add('hidden');
    } else if (mode === 'items') {
      // 查看單品模式：只顯示單品評分
      if (overallRatingSection) overallRatingSection.classList.add('hidden');
      if (commentsSection) commentsSection.classList.add('hidden');
      if (itemsSection) itemsSection.classList.remove('hidden');
    }
    
    // 更新 modal 中的貼文圖片
    const modalImage = document.getElementById('outfit-modal-image');
    if (modalImage && outfit) {
      modalImage.src = outfit.image_url || '';
    }
    
    // 更新右側的目前評分顯示
    if (outfit) {
      const avgRating = parseFloat(outfit.avg_rating) || 0;
      const ratingCount = outfit.rating_count || outfit.comment_count || 0;
      const fullStars = Math.floor(avgRating);
      const hasHalfStar = (avgRating % 1) >= 0.5;
      const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
      
      const starsHTML = '★'.repeat(fullStars) + (hasHalfStar ? '⯨' : '') + '☆'.repeat(emptyStars);
      
      const currentAvgRatingEl = document.getElementById('current-avg-rating');
      const currentAvgRatingValueEl = document.getElementById('current-avg-rating-value');
      const currentRatingCountEl = document.getElementById('current-rating-count');
      
      if (currentAvgRatingEl) {
        currentAvgRatingEl.textContent = starsHTML;
      }
      if (currentAvgRatingValueEl) {
        currentAvgRatingValueEl.textContent = avgRating.toFixed(1);
      }
      if (currentRatingCountEl) {
        currentRatingCountEl.textContent = `(${ratingCount} 評分)`;
      }
    }
    
    const res = await fetch(`/share/api/outfits/${outfitId}/comments`);
    const comments = await res.json();

    // 根據模式加載不同的內容
    if (mode === 'comment') {
      // 評論模式：加載評論內容
      const content = document.getElementById('comments-content');
      
      if (comments.length === 0) {
        content.innerHTML = `
          <div class="text-center py-8 text-subtle-light dark:text-subtle-dark">
            <span class="material-symbols-outlined text-4xl mb-2">chat_bubble_outline</span>
            <p>尚無評論</p>
          </div>
        `;
      } else {
        content.innerHTML = comments.map(comment => `
          <div class="mb-4 pb-4 border-b border-secondary-light dark:border-secondary-dark last:border-b-0">
            <div class="flex items-start gap-3">
              <!-- 用戶頭像/圖片 -->
              <div class="flex-shrink-0">
                ${comment.img_url ? 
                  `<img src="${comment.img_url}" alt="user avatar" class="h-12 w-12 rounded-full object-cover border-2 border-primary/20">` : 
                  `<div class="h-12 w-12 rounded-full bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center">
                    <span class="material-symbols-outlined text-primary">person</span>
                  </div>`
                }
              </div>
              
              <!-- 評論內容 -->
              <div class="flex-1">
                <!-- 用戶名和時間 -->
                <div class="flex items-center justify-between mb-2">
                  <div>
                    <p class="font-medium text-sm">${comment.user_name || '匿名用戶'}</p>
                    <p class="text-xs text-subtle-light dark:text-subtle-dark">${new Date(comment.created_at).toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                  </div>
                  <!-- 評分星星（右上角） -->
                  <div class="flex items-center gap-1">
                    <span style="color: #FFD700; font-size: 14px;">${renderStarsDisplay(comment.rating || 0)}</span>
                    <span class="text-sm font-bold text-primary">${(comment.rating || 0).toFixed(1)}</span>
                  </div>
                </div>
                
                <!-- 評論文字 -->
                ${comment.comment_text ? 
                  `<p class="text-sm text-text-light dark:text-text-dark leading-relaxed">${comment.comment_text}</p>` : 
                  `<p class="text-sm text-subtle-light dark:text-subtle-dark italic">未留下評論文字</p>`
                }
              </div>
            </div>
          </div>
        `).join('');
      }

      selectedRating = 0;
      if (modalRatingValue) modalRatingValue.value = 0;
      if (modalStars && modalStars.length) modalStars.forEach(s => s.classList.remove('active'));

      // Attach interactive listeners for comment stars
      attachCommentStarListeners();
      
      // 初始化新增評論功能
      initAddCommentForm();
    } else if (mode === 'items') {
      // 單品模式：加載單品評分
      const itemsContent = document.getElementById('items-content');
      itemsContent.innerHTML = comments.map(comment => `
        <div class="mb-4 p-4 border border-secondary-light dark:border-secondary-dark rounded-lg flex gap-4">
          <!-- 左邊：單品圖片 -->
          <div class="flex-shrink-0">
            ${comment.img_url ? 
              `<img src="${comment.img_url}" alt="item" class="w-24 h-24 object-cover rounded-lg" />` : 
              `<div class="w-24 h-24 rounded-lg bg-secondary-light dark:bg-secondary-dark flex items-center justify-center">
                <span class="material-symbols-outlined text-4xl text-subtle-light">checkroom</span>
              </div>`
            }
          </div>
          
          <!-- 右邊：評分區域 -->
          <div class="flex-1 flex flex-col justify-between">
            <!-- 目前評分（和星星、分數同一行） -->
            <div class="flex items-center gap-2 mb-3">
              <p class="text-sm text-subtle-light dark:text-subtle-dark">目前評分：</p>
              <span style="color: #FFD700; font-size: 16px;">${renderStarsDisplay(comment.rating || 0)}</span>
              <span class="font-bold text-primary">${(comment.rating || 0).toFixed(1)}</span>
            </div>
            
            <!-- 給予評分 -->
            <div>
              <p class="text-sm text-subtle-light dark:text-subtle-dark mb-2">給予評分：</p>
              <div class="comment-rating flex gap-1" data-comment-id="${comment.id}" data-comment-rating="${comment.rating}" data-outfit-id="${outfitId}">
                ${renderStars(0, 'large', true)}
              </div>
            </div>
          </div>
        </div>
      `).join('');

      // Attach interactive listeners for item stars
      attachCommentStarListeners();
    }

  } catch (err) {
    console.error('Error loading comments:', err);
  }
}

// Helper function to render display-only stars
function renderStarsDisplay(rating) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = (rating % 1) >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
  return '★'.repeat(fullStars) + (hasHalfStar ? '⯨' : '') + '☆'.repeat(emptyStars);
}

// ===== Add Comment Form =====
let newCommentRating = 0;

function initAddCommentForm() {
  const addRatingBtn = document.getElementById('add-rating-btn');
  const addCommentForm = document.getElementById('add-comment-form');
  const cancelBtn = document.getElementById('cancel-new-comment');
  const submitBtn = document.getElementById('submit-new-comment');
  const ratingStars = document.querySelectorAll('.new-comment-star');
  const ratingText = document.getElementById('new-comment-rating-text');
  const commentText = document.getElementById('new-comment-text');
  
  const ratingTexts = ['請選擇評分', '很差', '普通', '不錯', '很好', '超棒!'];
  
  if (!addRatingBtn || !addCommentForm) return;
  
  // 重置表單
  const resetForm = () => {
    newCommentRating = 0;
    ratingStars.forEach(s => {
      s.style.color = '#888888';
      s.textContent = '☆';
    });
    if (ratingText) {
      ratingText.textContent = '請選擇評分';
      ratingText.classList.remove('text-primary');
    }
    if (commentText) commentText.value = '';
  };
  
  // 顯示表單
  addRatingBtn.addEventListener('click', () => {
    addCommentForm.classList.remove('hidden');
    addRatingBtn.classList.add('hidden');
    resetForm();
  });
  
  // 取消按鈕
  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      addCommentForm.classList.add('hidden');
      addRatingBtn.classList.remove('hidden');
    });
  }
  
  // 初始隱藏表單
  addCommentForm.classList.add('hidden');
  addRatingBtn.classList.remove('hidden');
  
  // 星星互動
  ratingStars.forEach(star => {
    star.addEventListener('click', () => {
      newCommentRating = parseInt(star.dataset.rating);
      ratingStars.forEach((s, idx) => {
        if (idx < newCommentRating) {
          s.style.color = '#FFD700';
          s.textContent = '★';
        } else {
          s.style.color = '#888888';
          s.textContent = '☆';
        }
      });
      if (ratingText) {
        ratingText.textContent = ratingTexts[newCommentRating];
        ratingText.classList.add('text-primary');
      }
    });
    
    star.addEventListener('mouseenter', () => {
      const hoverRating = parseInt(star.dataset.rating);
      ratingStars.forEach((s, idx) => {
        if (idx < hoverRating) {
          s.style.color = '#FFD700';
          s.textContent = '★';
        } else if (idx >= newCommentRating) {
          s.style.color = '#888888';
          s.textContent = '☆';
        }
      });
      if (ratingText && newCommentRating === 0) {
        ratingText.textContent = ratingTexts[hoverRating];
      }
    });
  });
  
  // 滑鼠離開評分區域
  const ratingContainer = document.getElementById('new-comment-rating');
  if (ratingContainer) {
    ratingContainer.addEventListener('mouseleave', () => {
      ratingStars.forEach((s, idx) => {
        if (idx < newCommentRating) {
          s.style.color = '#FFD700';
          s.textContent = '★';
        } else {
          s.style.color = '#888888';
          s.textContent = '☆';
        }
      });
      if (ratingText && newCommentRating === 0) {
        ratingText.textContent = '請選擇評分';
        ratingText.classList.remove('text-primary');
      }
    });
  }
  
  // 提交評論與評分
  if (submitBtn) {
    submitBtn.addEventListener('click', async () => {
      if (!currentOutfitId) {
        alert('無法提交評論，請重新打開');
        return;
      }
      
      if (newCommentRating === 0) {
        alert('請選擇評分');
        return;
      }
      
      const text = commentText ? commentText.value.trim() : '';
      
      try {
        const requests = [];
        
        // 1. 提交評論（總體評分）
        requests.push(
          fetch(`/share/api/outfits/${currentOutfitId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              rating: newCommentRating,
              comment_text: text || null
            })
          })
        );
        
        // 2. 提交單品評分（如果有）
        for (const [commentId, rating] of changedCommentRatings.entries()) {
          requests.push(
            fetch(`/share/api/outfits/${currentOutfitId}/comments/${commentId}/rate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ rating: rating })
            })
          );
        }
        
        const results = await Promise.all(requests);
        
        if (results.every(r => r.ok)) {
          alert('評論已提交！');
          changedCommentRatings.clear();
          // 隱藏表單並顯示按鈕
          if (addCommentForm) addCommentForm.classList.add('hidden');
          if (addRatingBtn) addRatingBtn.classList.remove('hidden');
          // 重新載入
          const outfit = await fetch('/share/api/outfits').then(r => r.json()).then(outfits => outfits.find(o => o.id == currentOutfitId));
          await loadComments(currentOutfitId, outfit, 'comment');
        } else {
          alert('部分提交失敗');
        }
      } catch (err) {
        alert('錯誤: ' + err.message);
      }
    });
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

// ===== Submit Item Ratings =====
document.addEventListener('DOMContentLoaded', () => {
  const submitItemRatingsBtn = document.getElementById('submit-item-ratings');
  if (submitItemRatingsBtn) {
    submitItemRatingsBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      if (!currentOutfitId) {
        alert('無法提交評分，請先選擇穿搭');
        return;
      }
      
      if (changedCommentRatings.size === 0) {
        alert('請至少給予一個單品評分');
        return;
      }

      try {
        const requests = [];
        
        // 提交單品評分
        for (const [commentId, rating] of changedCommentRatings.entries()) {
          requests.push(
            fetch(`/share/api/outfits/${currentOutfitId}/comments/${commentId}/rate`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ rating: rating })
            })
          );
        }

        const results = await Promise.all(requests);
        if (results.every(r => r.ok)) {
          alert('評分已提交！');
          changedCommentRatings.clear();
          modal.classList.add('hidden');
          await loadOutfits();
        } else {
          alert('部分評分提交失敗');
        }
      } catch (err) {
        alert('錯誤: ' + err.message);
      }
    });
  }
});

// ===== Initial Load =====
loadOutfits();