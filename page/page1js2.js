  const toggleBtn = document.getElementById('toggleBtn');
  const dialog = document.getElementById('dialog');

  let isOpen = false;

  toggleBtn.addEventListener('click', () => {
    isOpen = !isOpen;
    dialog.classList.toggle('active', isOpen);
    toggleBtn.textContent = isOpen ? '隱藏對話框' : '展開對話框';
  });
