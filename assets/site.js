'use strict';

// Search and categories use the same generated note list.
const searchInput = document.querySelector('#note-search');
if (searchInput) {
  let currentCategory = 'all';
  const cards = Array.from(document.querySelectorAll('[data-note]'));
  const filters = Array.from(document.querySelectorAll('[data-filter]'));
  const updateResults = () => {
    const query = searchInput.value.trim().toLocaleLowerCase();
    let count = 0;
    cards.forEach(card => {
      const match = (currentCategory === 'all' || card.dataset.category === currentCategory) && card.dataset.search.includes(query);
      card.hidden = !match;
      if (match) count += 1;
    });
    document.querySelector('#result-count').textContent = `${count} 篇筆記`;
    document.querySelector('#empty-result').hidden = count > 0;
    filters.forEach(button => {
      const selected = button.dataset.filter === currentCategory;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
  };
  searchInput.addEventListener('input', updateResults);
  filters.forEach(button => button.addEventListener('click', () => {
    currentCategory = button.dataset.filter;
    updateResults();
  }));
  document.querySelector('#clear-search').addEventListener('click', () => {
    searchInput.value = '';
    currentCategory = 'all';
    updateResults();
    searchInput.focus();
  });
}

const queueSlots = document.querySelector('#queue-slots');
if (queueSlots) {
  const queue = [];
  let sequence = 1;
  const message = document.querySelector('#queue-message');
  const paint = (text, warning = false) => {
    Array.from(queueSlots.children).forEach((slot, i) => {
      slot.textContent = queue[i] === undefined ? '—' : String(queue[i]);
      slot.classList.toggle('filled', queue[i] !== undefined);
      slot.setAttribute('aria-label', `第 ${i + 1} 格：${queue[i] === undefined ? '空' : queue[i]}`);
    });
    document.querySelector('#queue-count').textContent = `${queue.length} / 5 筆`;
    message.textContent = text;
    message.classList.toggle('warning', warning);
  };
  document.querySelector('#enqueue').addEventListener('click', () => {
    if (queue.length === 5) {
      paint('傳送失敗：Queue 已滿。等待時間是 0，原本的 5 筆資料保留。', true);
      return;
    }
    const value = sequence++;
    queue.push(value);
    paint(`已放入 ${value}，排在 Queue 尾端。`);
  });
  document.querySelector('#dequeue').addEventListener('click', () => {
    if (!queue.length) {
      paint('接收失敗：Queue 是空的。等待時間是 0，立即回傳。', true);
      return;
    }
    const value = queue.shift();
    paint(`已取出最早放入的 ${value}，現在有 ${5 - queue.length} 個空位。`);
  });
  document.querySelector('#reset-queue').addEventListener('click', () => {
    queue.length = 0;
    sequence = 1;
    paint('已重設。Queue 是空的，下一筆資料從 1 開始。');
  });
}

document.querySelectorAll('.copy-code').forEach(button => {
  button.addEventListener('click', async () => {
    const code = button.closest('.code-window').querySelector('code').textContent;
    try {
      await navigator.clipboard.writeText(code);
      button.textContent = '已複製';
    } catch {
      button.textContent = '請選取下方程式碼複製';
    }
  });
});
