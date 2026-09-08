(() => {
  const clock = document.createElement('div');
  clock.className = 'taiwan-clock';
  clock.setAttribute('aria-live', 'polite');
  document.body.prepend(clock);
  const formatter = new Intl.DateTimeFormat('zh-TW', {
    timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
  });
  const update = () => { clock.textContent = `台灣時間／Giờ Đài Loan：${formatter.format(new Date())}`; };
  update();
  setInterval(update, 1000);
})();
