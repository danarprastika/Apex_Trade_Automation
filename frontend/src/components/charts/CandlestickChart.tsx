import ReactECharts from 'echarts-for-react'

export type CandlePoint = [number, number, number, number, number]

export function CandlestickChart({ data }: { data: CandlePoint[] }) {
  const option = {
    backgroundColor: 'transparent',
    dataset: { source: data },
    grid: { left: 8, right: 24, top: 16, bottom: 24 },
    xAxis: { type: 'time', axisLabel: { color: '#94a3b8' } },
    yAxis: { scale: true, axisLabel: { color: '#94a3b8' } },
    series: [
      { type: 'candlestick', itemStyle: { color: '#22c55e', color0: '#ef4444', borderColor: '#22c55e', borderColor0: '#ef4444' } },
    ],
    tooltip: { trigger: 'axis' },
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: 420 }}
      opts={{ renderer: 'canvas' }}
    />
  )
}
