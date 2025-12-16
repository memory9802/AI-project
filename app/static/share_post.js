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

// ===== Image Lightbox =====
const imageLightbox = document.getElementById('image-lightbox');
const lightboxImage = document.getElementById('lightbox-image');
const closeLightboxBtn = document.getElementById('close-lightbox');

function openImageLightbox(imageUrl) {
  lightboxImage.src = imageUrl;
  imageLightbox.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeImageLightbox() {
  imageLightbox.classList.add('hidden');
  document.body.style.overflow = '';
}

if (closeLightboxBtn) {
  closeLightboxBtn.addEventListener('click', closeImageLightbox);
}

// Close lightbox when clicking on background
imageLightbox.addEventListener('click', (e) => {
  if (e.target === imageLightbox || e.target === lightboxImage) {
    closeImageLightbox();
  }
});

// Close lightbox with ESC key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !imageLightbox.classList.contains('hidden')) {
    closeImageLightbox();
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
const mainPreviewContainer = document.getElementById('main-preview-container');
const removeMainImageBtn = document.getElementById('remove-main-image');
const descriptionInput = document.getElementById('description-input');
const descriptionCount = document.getElementById('description-count');
const descriptionError = document.getElementById('description-error');
const uploadLoading = document.getElementById('upload-loading');
const uploadSuccess = document.getElementById('upload-success');
const submitBtn = document.getElementById('submit-btn');
const submitText = document.getElementById('submit-text');
const submitSpinner = document.getElementById('submit-spinner');
const uploadProgress = document.getElementById('upload-progress');

// Items (multiple single-item photos)
const itemsInput = document.getElementById('items-input');
const chooseItemsBtn = document.getElementById('choose-items-btn');
const itemsPreview = document.getElementById('items-preview');
const itemsUploadArea = document.getElementById('items-upload-area');

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

// File validation
function validateFile(file, maxSizeMB = 5) {
  if (!file) return { valid: false, error: '請選擇檔案' };
  
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: '僅支援 JPG, PNG, GIF 格式' };
  }
  
  const maxSize = maxSizeMB * 1024 * 1024;
  if (file.size > maxSize) {
    return { valid: false, error: `檔案大小不能超過 ${maxSizeMB}MB` };
  }
  
  return { valid: true };
}

// Show validation error
function showError(element, message) {
  element.textContent = message;
  element.classList.remove('hidden');
}

function hideError(element) {
  element.classList.add('hidden');
}

// Description character count
if (descriptionInput && descriptionCount) {
  descriptionInput.addEventListener('input', () => {
    const count = descriptionInput.value.length;
    descriptionCount.textContent = `${count}/200`;
    if (count > 180) {
      descriptionCount.classList.add('text-orange-500');
    } else {
      descriptionCount.classList.remove('text-orange-500');
    }
  });
}

// Remove main image
if (removeMainImageBtn) {
  removeMainImageBtn.addEventListener('click', () => {
    imageInput.value = '';
    mainPreviewContainer.classList.add('hidden');
  });
}

// Items selection area - click and drag/drop support like main upload
if (itemsUploadArea && itemsInput) {
  itemsUploadArea.addEventListener('click', () => itemsInput.click());
  
  itemsUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    itemsUploadArea.classList.add('bg-primary/10');
  });

  itemsUploadArea.addEventListener('dragleave', () => {
    itemsUploadArea.classList.remove('bg-primary/10');
  });

  itemsUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    itemsUploadArea.classList.remove('bg-primary/10');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      itemsInput.files = files;
      displayItemPreviews();
    }
  });
}

// Legacy button support (if still exists)
if (chooseItemsBtn && itemsInput) {
  chooseItemsBtn.addEventListener('click', () => itemsInput.click());
}

// Display previews for multiple item files
if (itemsInput) {
  itemsInput.addEventListener('change', displayItemPreviews);
}

function displayItemPreviews() {
  if (!itemsPreview) return;
  itemsPreview.innerHTML = '';
  const files = itemsInput.files;
  if (!files || files.length === 0) return;

  // Validate all files first
  const validFiles = [];
  Array.from(files).forEach((file) => {
    const validation = validateFile(file);
    if (validation.valid) {
      validFiles.push(file);
    } else {
      alert(`檔案 "${file.name}": ${validation.error}`);
    }
  });

  // Update input with only valid files
  const dt = new DataTransfer();
  validFiles.forEach(f => dt.items.add(f));
  itemsInput.files = dt.files;

  // Display previews
  validFiles.forEach((file, idx) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const div = document.createElement('div');
      div.className = 'relative w-full h-24 overflow-hidden rounded-lg border border-secondary-light dark:border-secondary-dark';
      div.innerHTML = `
        <img src="${e.target.result}" class="w-full h-24 object-cover rounded-lg" />
        <button type="button" data-idx="${idx}" class="remove-item absolute top-1 right-1 bg-black/60 hover:bg-black/80 text-white rounded-full p-1 text-xs">✕</button>
        <div class="absolute bottom-1 left-1 bg-black/60 text-white text-xs px-2 py-1 rounded">${idx + 1}</div>
      `;
      itemsPreview.appendChild(div);

      // attach remove handler
      div.querySelector('.remove-item').addEventListener('click', (ev) => {
        ev.preventDefault();
        removeItemAtIndex(parseInt(ev.currentTarget.dataset.idx));
      });
    };
    reader.readAsDataURL(file);
  });
}

function removeItemAtIndex(index) {
  const dt = new DataTransfer();
  const files = Array.from(itemsInput.files || []);
  files.forEach((f, i) => { if (i !== index) dt.items.add(f); });
  itemsInput.files = dt.files;
  displayItemPreviews();
}

imageInput.addEventListener('change', displayPreview);

function displayPreview() {
  const file = imageInput.files[0];
  if (!file) {
    mainPreviewContainer.classList.add('hidden');
    return;
  }
  
  const validation = validateFile(file);
  if (!validation.valid) {
    alert(validation.error);
    imageInput.value = '';
    mainPreviewContainer.classList.add('hidden');
    return;
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImage.src = e.target.result;
    mainPreviewContainer.classList.remove('hidden');
  };
  reader.readAsDataURL(file);
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

// ===== Update Outfit Rating =====
async function updateOutfitRating(outfitId, newRating, isNewComment) {
  try {
    // 獲取原始貼文資料
    const res = await fetch('/share/api/outfits');
    const outfits = await res.json();
    const outfit = outfits.find(o => o.id == outfitId);
    
    if (!outfit) return;
    
    // 獲取後端所有評論來計算基礎評分
    const commentsRes = await fetch(`/share/api/outfits/${outfitId}/comments`);
    const backendComments = await commentsRes.json();
    
    // 計算後端評論的總評分
    const backendTotalRating = backendComments.reduce((sum, c) => sum + (c.rating || 0), 0);
    const backendCommentCount = backendComments.length;
    
    // 獲取用戶提交的評論
    const commentsKey = `outfit_comments_${outfitId}`;
    const storedComments = localStorage.getItem(commentsKey);
    let userComments = [];
    
    if (storedComments) {
      userComments = JSON.parse(storedComments);
    }
    
    // 計算用戶評論的總評分
    const userTotalRating = userComments.reduce((sum, c) => sum + (c.rating || 0), 0);
    const userCommentCount = userComments.length;
    
    // 計算總評分和總人數
    const totalRating = backendTotalRating + userTotalRating;
    const totalCount = backendCommentCount + userCommentCount;
    
    // 計算平均評分：總評分 / 評論人數
    const avgRating = totalCount > 0 ? totalRating / totalCount : 0;
    
    // 儲存到 localStorage
    const storageKey = `outfit_rating_${outfitId}`;
    localStorage.setItem(storageKey, JSON.stringify({
      total_rating: totalRating,
      comment_count: totalCount,
      avg_rating: avgRating
    }));
    
  } catch (err) {
    console.error('更新評分失敗:', err);
  }
}

// ===== Upload Form =====
document.getElementById('upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  // Reset previous errors
  hideError(descriptionError);
  
  // Validation
  const file = imageInput.files[0];
  const description = descriptionInput.value.trim();
  
  let hasError = false;
  
  if (!file) {
    alert('請選擇穿搭照片');
    hasError = true;
  }
  
  if (!description) {
    showError(descriptionError, '請填寫穿搭描述');
    hasError = true;
  }
  
  if (hasError) {
    return;
  }

  // Show loading state
  setLoadingState(true);
  
  const formData = new FormData();
  formData.append('image', file);
  formData.append('description', description);
  formData.append('tags', selectedTags.join(','));
  
  // append item photos (multiple)
  if (itemsInput && itemsInput.files && itemsInput.files.length > 0) {
    Array.from(itemsInput.files).forEach(f => {
      formData.append('items', f);
    });
  }

  try {
    // Simulate progress for better UX
    updateProgress(30);
    
    const res = await fetch('/share/api/outfits', {
      method: 'POST',
      body: formData
    });

    updateProgress(80);
    
    const result = await res.json();
    
    if (res.ok && result.success) {
      updateProgress(100);
      setTimeout(() => {
        showSuccessState();
        loadOutfits(); // Refresh the feed
      }, 500);
    } else {
      throw new Error(result.message || '上傳失敗');
    }
  } catch (err) {
    console.error('Upload error:', err);
    setLoadingState(false);
    alert('上傳失敗: ' + err.message);
  }
});

function setLoadingState(loading) {
  if (loading) {
    submitBtn.disabled = true;
    submitText.textContent = '上傳中...';
    submitSpinner.classList.remove('hidden');
    uploadLoading.classList.remove('hidden');
    updateProgress(10);
  } else {
    submitBtn.disabled = false;
    submitText.textContent = '上傳穿搭';
    submitSpinner.classList.add('hidden');
    uploadLoading.classList.add('hidden');
    updateProgress(0);
  }
}

function updateProgress(percent) {
  if (uploadProgress) {
    uploadProgress.style.width = `${percent}%`;
  }
}

function showSuccessState() {
  document.getElementById('upload-form').classList.add('hidden');
  uploadLoading.classList.add('hidden');
  uploadSuccess.classList.remove('hidden');
}

function resetUploadForm() {
  // Reset form
  document.getElementById('upload-form').reset();
  mainPreviewContainer.classList.add('hidden');
  if (itemsPreview) itemsPreview.innerHTML = '';
  if (itemsInput) itemsInput.value = '';
  
  // Reset tags
  selectedTags = [];
  document.querySelectorAll('.tag-btn').forEach(btn => {
    btn.classList.remove('bg-primary/30', 'text-primary');
  });
  updateSelectedTags();
  
  // Reset character count
  if (descriptionCount) descriptionCount.textContent = '0/200';
  
  // Hide errors
  hideError(descriptionError);
  
  // Reset states
  setLoadingState(false);
  document.getElementById('upload-form').classList.remove('hidden');
  uploadSuccess.classList.add('hidden');
}

// Upload another button
document.getElementById('upload-another')?.addEventListener('click', () => {
  resetUploadForm();
});

// Close modal also resets form
if (closeUploadBtn) {
  closeUploadBtn.addEventListener('click', () => {
    uploadModal.classList.add('hidden');
    setTimeout(resetUploadForm, 300); // Reset after animation
  });
}

// ===== Load Outfits =====
async function loadOutfits() {
  try {
    const res = await fetch('/share/api/outfits');
    let outfits = await res.json();
    
    // 更新每個貼文的評分和評論數（從 localStorage 讀取）
    outfits = outfits.map(outfit => {
      const storageKey = `outfit_rating_${outfit.id}`;
      const ratingData = localStorage.getItem(storageKey);
      
      if (ratingData) {
        const parsed = JSON.parse(ratingData);
        return {
          ...outfit,
          avg_rating: parsed.avg_rating,
          comment_count: parsed.comment_count
        };
      }
      return outfit;
    });

    const container = document.getElementById('outfits-container');
    container.innerHTML = outfits.map(outfit => `
    <div class="bg-white dark:bg-secondary-dark rounded-lg overflow-hidden shadow-sm border border-secondary-light dark:border-secondary-dark">
      <!-- Outfit Image -->
      <div class="relative w-full cursor-pointer group" style="padding-bottom: 125%;" onclick="openImageLightbox('${outfit.image_url}')">
        <img src="${outfit.image_url}" alt="outfit" class="absolute inset-0 w-full h-full object-cover transition-transform group-hover:scale-105" />
        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
          <span class="material-symbols-outlined text-white text-5xl opacity-0 group-hover:opacity-100 transition-opacity">zoom_in</span>
        </div>
      </div>

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
    
    // 根據模式決定 API endpoint
    const endpoint = mode === 'items' ? 
      `/share/api/outfits/${outfitId}/items` : 
      `/share/api/outfits/${outfitId}/comments`;
    
    const res = await fetch(endpoint);
    let comments = await res.json();
    
    // 如果是評論模式，合併後端評論和用戶提交的評論
    if (mode === 'comment') {
      const userCommentsKey = `outfit_comments_${outfitId}`;
      const storedUserComments = localStorage.getItem(userCommentsKey);
      if (storedUserComments) {
        const userComments = JSON.parse(storedUserComments);
        // 將用戶評論添加到列表末尾
        comments = [...comments, ...userComments];
      }
    }

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
              <!-- 評論內容（移除頭像） -->
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
                  `<p class="text-sm text-subtle-light dark:text-subtle-dark italic"> </p>`
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
      itemsContent.innerHTML = comments.map(comment => {
        // 檢查 localStorage 是否有更新的評分
        const storageKey = `item_${outfitId}_${comment.id}`;
        const storedData = localStorage.getItem(storageKey);
        let displayRating = comment.rating || 0;
        let displayRatingCount = comment.rating_count || 0;
        
        if (storedData) {
          const parsed = JSON.parse(storedData);
          displayRating = parsed.rating;
          displayRatingCount = parsed.rating_count;
        }
        
        return `
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
                <span style="color: #FFD700; font-size: 16px;">${renderStarsDisplay(displayRating)}</span>
                <span class="font-bold text-primary">${displayRating.toFixed(1)}</span>
                <span class="text-xs text-subtle-light dark:text-subtle-dark">(${displayRatingCount} 評分)</span>
              </div>
              
              <!-- 給予評分 -->
              <div>
                <div class="flex items-center gap-2 mb-2">
                  <p class="text-sm text-subtle-light dark:text-subtle-dark">給予評分：</p>
                  ${localStorage.getItem(`user_rating_${outfitId}_${comment.id}`) ? 
                    '<span class="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">已評分</span>' : 
                    ''}
                </div>
                <div class="comment-rating flex gap-1" 
                     data-comment-id="${comment.id}" 
                     data-comment-rating="${comment.rating}" 
                     data-original-rating="${comment.rating}"
                     data-rating-count="${comment.rating_count}"
                     data-user-rating="${localStorage.getItem(`user_rating_${outfitId}_${comment.id}`) || '0'}"
                     data-outfit-id="${outfitId}">
                  ${renderStars(0, 'large', true)}
                </div>
              </div>
            </div>
          </div>
        `;
      }).join('');

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
    // 檢查是否有保存的評論記錄
    const savedComment = localStorage.getItem(`user_comment_${currentOutfitId}`);
    if (savedComment) {
      const parsed = JSON.parse(savedComment);
      newCommentRating = parsed.rating || 0;
      
      // 恢復星星顯示
      ratingStars.forEach((s, idx) => {
        if (idx < newCommentRating) {
          s.style.color = '#FFD700';
          s.textContent = '★';
        } else {
          s.style.color = '#888888';
          s.textContent = '☆';
        }
      });
      
      // 恢復評分文字
      if (ratingText && newCommentRating > 0) {
        ratingText.textContent = ratingTexts[newCommentRating];
        ratingText.classList.add('text-primary');
      }
      
      // 恢復評論文字
      if (commentText && parsed.comment_text) {
        commentText.value = parsed.comment_text;
      }
      
      // 恢復匿名選項
      const anonymousCheckbox = document.getElementById('anonymous-comment');
      if (anonymousCheckbox && parsed.is_anonymous !== undefined) {
        anonymousCheckbox.checked = parsed.is_anonymous;
      }
    } else {
      // 沒有保存記錄，重置為空
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
      const anonymousCheckbox = document.getElementById('anonymous-comment');
      if (anonymousCheckbox) anonymousCheckbox.checked = false;
    }
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
      
      // 驗證：評分為必選
      if (newCommentRating === 0) {
        alert('請選擇評分（必填）');
        return;
      }
      
      const text = commentText ? commentText.value.trim() : '';
      const anonymousCheckbox = document.getElementById('anonymous-comment');
      const isAnonymous = anonymousCheckbox ? anonymousCheckbox.checked : false;
      
      // Demo 版本：本地儲存評論
      try {
        // 獲取當前用戶名（從登入系統獲取）
        const username = window.currentUser?.username || '用戶';
        const displayName = isAnonymous ? '匿名用戶' : username;
        
        // 創建新評論對象
        const newComment = {
          id: Date.now(), // 使用時間戳作為臨時 ID
          user_name: displayName,
          rating: newCommentRating,
          comment_text: text || '',
          created_at: new Date().toISOString()
        };
        
        // 保存到 localStorage（用於記憶評論）
        localStorage.setItem(`user_comment_${currentOutfitId}`, JSON.stringify({
          rating: newCommentRating,
          comment_text: text,
          is_anonymous: isAnonymous
        }));
        
        // 保存新評論到 localStorage（用於顯示在列表中）
        const commentsKey = `outfit_comments_${currentOutfitId}`;
        let existingComments = [];
        const stored = localStorage.getItem(commentsKey);
        if (stored) {
          existingComments = JSON.parse(stored);
        }
        
        // 檢查是否已有用戶的評論（更新而不是新增）
        const existingIndex = existingComments.findIndex(c => c.user_name === displayName);
        if (existingIndex >= 0) {
          existingComments[existingIndex] = newComment;
        } else {
          existingComments.push(newComment);
        }
        
        localStorage.setItem(commentsKey, JSON.stringify(existingComments));
        
        // 更新貼文的平均評分和評論人數
        await updateOutfitRating(currentOutfitId, newCommentRating, existingIndex < 0);
        
        // 重新載入貼文列表以顯示更新後的評分
        await loadOutfits();
        
        // 所有操作完成後，只顯示一次成功通知
        alert('評論已提交！');
        
        // 通知按掉後，清除資料並關閉視窗
        changedCommentRatings.clear();
        
        // 隱藏表單並顯示按鈕
        if (addCommentForm) addCommentForm.classList.add('hidden');
        if (addRatingBtn) addRatingBtn.classList.remove('hidden');
        
        // 關閉評論視窗
        modal.classList.add('hidden');
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

    // 檢查是否有用戶之前的評分記錄
    const savedUserRating = parseInt(container.dataset.userRating) || 0;
    
    // 初始化視覺狀態：如果有保存的評分則顯示，否則為 0
    setVisual(savedUserRating);
    container.dataset.userRating = savedUserRating;
    
    // 如果有保存的評分，則加入到 changedCommentRatings（這樣可以重新提交修改）
    if (savedUserRating > 0) {
      changedCommentRatings.set(commentId, savedUserRating);
    }

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

// ===== Submit Item Ratings (Demo Version with Local Storage) =====
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

      // Demo版本：本地更新評分數據
      try {
        // 更新本地儲存的評分數據
        for (const [itemId, newRating] of changedCommentRatings.entries()) {
          // 從 DOM 獲取原始評分數據
          const itemContainer = document.querySelector(`.comment-rating[data-comment-id="${itemId}"]`);
          if (itemContainer) {
            const originalRating = parseFloat(itemContainer.dataset.originalRating) || 0;
            const ratingCount = parseInt(itemContainer.dataset.ratingCount) || 0;
            
            // 計算新的平均評分：(原總分 + 新評分) / (原人數 + 1)
            const totalScore = originalRating * ratingCount;
            const newTotalScore = totalScore + newRating;
            const newRatingCount = ratingCount + 1;
            const newAverageRating = newTotalScore / newRatingCount;
            
            // 儲存平均評分到 localStorage (demo用途)
            const storageKey = `item_${currentOutfitId}_${itemId}`;
            localStorage.setItem(storageKey, JSON.stringify({
              rating: newAverageRating,
              rating_count: newRatingCount
            }));
            
            // 儲存用戶個人評分（用於下次顯示已評分狀態）
            const userRatingKey = `user_rating_${currentOutfitId}_${itemId}`;
            localStorage.setItem(userRatingKey, newRating.toString());
          }
        }
        
        alert('評分已提交！');
        changedCommentRatings.clear();
        modal.classList.add('hidden');
        
        // 重新載入以顯示更新後的評分
        await loadOutfits();
      } catch (err) {
        alert('錯誤: ' + err.message);
      }
    });
  }
});

// ===== Initial Load =====
loadOutfits();