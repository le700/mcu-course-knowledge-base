(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // --- Chart: Risk Severity Distribution ---
  var chart1 = echarts.init(document.getElementById('chart-risk'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: { trigger: 'item', appendToBody: true },
    legend: { bottom: 0, textStyle: { color: ink } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      label: { color: ink, formatter: '{b}\n{d}%' },
      data: [
        { value: 4, name: 'P0 致命', itemStyle: { color: '#e74c3c' } },
        { value: 4, name: 'P1 严重', itemStyle: { color: '#e67e22' } },
        { value: 5, name: 'P2 中等', itemStyle: { color: '#f1c40f' } },
        { value: 3, name: 'P3 轻微', itemStyle: { color: '#3498db' } }
      ]
    }]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart: Requirement Coverage ---
  var chart2 = echarts.init(document.getElementById('chart-req'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    grid: { left: 120, right: 40, top: 20, bottom: 20 },
    xAxis: { type: 'value', max: 100, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: {
      type: 'category',
      data: ['2.9 夜间模式', '2.8 紧急优先', '2.7 行人请求', '2.6 智能配时', '2.5 等待统计', '2.4 车流检测', '2.3 OLED显示', '2.2 倒计时', '2.1 基本交通灯'],
      axisLabel: { color: ink }
    },
    series: [{
      type: 'bar',
      data: [85, 80, 90, 95, 90, 95, 85, 95, 100],
      itemStyle: { color: accent },
      label: { show: true, position: 'right', formatter: '{c}%', color: ink }
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  // --- Chart: Acceptance Criteria ---
  var chart3 = echarts.init(document.getElementById('chart-accept'), null, { renderer: 'svg' });
  chart3.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    grid: { left: 120, right: 40, top: 20, bottom: 20 },
    xAxis: { type: 'value', max: 100, axisLabel: { color: muted }, splitLine: { lineStyle: { color: rule } } },
    yAxis: {
      type: 'category',
      data: ['验收7 编译加载', '验收6 夜间模式', '验收5 紧急模式', '验收4 行人请求', '验收3 车流配时', '验收2 数码管', '验收1 交通灯互锁'],
      axisLabel: { color: ink }
    },
    series: [{
      type: 'bar',
      data: [100, 90, 70, 75, 85, 90, 95],
      itemStyle: { color: accent2 },
      label: { show: true, position: 'right', formatter: '{c}%', color: ink },
      markLine: {
        silent: true,
        data: [{ xAxis: 80, label: { formatter: '合格线', color: muted }, lineStyle: { color: muted, type: 'dashed' } }]
      }
    }]
  });
  window.addEventListener('resize', function() { chart3.resize(); });
})();