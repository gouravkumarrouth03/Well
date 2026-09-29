export type Role = 'ADMIN' | 'OPERATIONS_MANAGER' | 'FIELD_ENGINEER'
export type Well = {
  id: string; name: string; status: string; oil: number; temp: number; pressure: number
  viscosity: number; spm: number; stroke: number; vfd: number; steam: number; sor: number
  efficiency: number; risk: 'NORMAL' | 'WARNING' | 'HIGH RISK' | 'CRITICAL'; rodLoad: number
  fillage: number; waterCut: number; fluidLevel: number; bop: number; steamPressure: number; energy: number
}

const seed = [
  ['BGL-001', 96, 58, 42, 1180, 7.2, 86, 45, 62, 3.6, 79, 'NORMAL'],
  ['BGL-002', 81, 55, 38, 1420, 7.5, 90, 48, 55, 4.0, 73, 'WARNING'],
  ['BGL-003', 73, 54, 36, 1550, 6.9, 84, 44, 51, 4.2, 70, 'WARNING'],
  ['BGL-004', 92, 61, 44, 980, 7.8, 90, 46, 68, 3.4, 84, 'NORMAL'],
  ['BGL-005', 64, 52, 34, 1780, 6.5, 82, 42, 48, 4.7, 66, 'HIGH RISK'],
  ['BGL-006', 87, 57, 40, 1260, 7.1, 86, 45, 61, 3.8, 77, 'NORMAL'],
  ['BGL-007', 78, 56, 39, 1350, 7.3, 88, 47, 59, 3.9, 75, 'NORMAL'],
  ['BGL-008', 69, 53, 35, 1660, 6.8, 84, 43, 50, 4.5, 68, 'WARNING'],
  ['BGL-009', 101, 63, 46, 890, 8.0, 92, 49, 72, 3.2, 87, 'NORMAL'],
  ['BGL-010', 75, 55, 37, 1470, 7.0, 86, 45, 57, 4.1, 72, 'NORMAL'],
  ['BGL-011', 83, 59, 41, 1100, 7.4, 88, 46, 64, 3.7, 80, 'NORMAL'],
  ['BGL-012', 57, 50, 32, 1940, 6.3, 80, 41, 44, 5.1, 62, 'HIGH RISK'],
  ['BGL-013', 71, 54, 36, 1580, 6.8, 84, 44, 52, 4.4, 69, 'WARNING'],
  ['BGL-014', 58, 49, 31, 2180, 7.5, 90, 48, 41, 5.4, 58, 'CRITICAL'],
  ['BGL-015', 94, 60, 43, 1020, 7.7, 90, 47, 69, 3.5, 83, 'NORMAL'],
  ['BGL-016', 77, 56, 38, 1390, 7.1, 86, 45, 58, 3.9, 74, 'NORMAL'],
  ['BGL-017', 68, 52, 34, 1740, 6.6, 82, 42, 49, 4.8, 65, 'HIGH RISK'],
  ['BGL-018', 89, 58, 41, 1160, 7.6, 88, 46, 65, 3.6, 81, 'NORMAL'],
  ['BGL-019', 62, 51, 33, 1860, 6.4, 80, 41, 46, 4.9, 63, 'WARNING'],
  ['BGL-020', 85, 57, 40, 1240, 7.2, 86, 45, 62, 3.8, 78, 'NORMAL'],
  ['BGL-021', 74, 54, 36, 1510, 6.9, 84, 44, 54, 4.2, 70, 'WARNING'],
  ['BGL-022', 98, 62, 45, 940, 7.9, 92, 48, 71, 3.3, 86, 'NORMAL'],
  ['BGL-023', 66, 52, 35, 1690, 6.7, 84, 43, 48, 4.6, 67, 'WARNING'],
  ['BGL-024', 80, 57, 39, 1280, 7.3, 86, 45, 60, 3.7, 78, 'NORMAL'],
] as const

export const wells: Well[] = seed.map((row, index) => ({
  id: row[0], name: `Baghewala ${String(index + 1).padStart(2, '0')}`,
  status: row[11] === 'CRITICAL' ? 'Attention' : 'Producing',
  oil: row[1], temp: row[2], pressure: row[3], viscosity: row[4], spm: row[5],
  stroke: row[6], vfd: row[7], steam: row[8], sor: row[9], efficiency: row[10],
  risk: row[11], rodLoad: row[11] === 'CRITICAL' ? 42.8 : 27 + (index * 7 % 12),
  fillage: row[11] === 'CRITICAL' ? 54 : 68 + (index * 3 % 19), waterCut: 21 + index % 17,
  fluidLevel: row[11] === 'CRITICAL' ? 286 : 180 + (index * 29 % 140), bop: row[3] + 18,
  steamPressure: 72 + (index * 3 % 18), energy: 38 + index % 12,
}))

export function authorizationHeaders(): Record<string, string> {
  const token = localStorage.getItem('baghewala_access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function fetchWellsFromApi(): Promise<Well[]> {
  const response = await fetch('/api/wells', { headers: authorizationHeaders() })
  if (!response.ok) throw new Error('Unable to load wells')
  const payload = await response.json() as { items: Array<Record<string, string | number>> }
  return payload.items.map(item => {
    const fallback = wells.find(well => well.id === item.id)
    if (!fallback) throw new Error(`Unknown well returned by API: ${item.id}`)
    return {
      ...fallback,
      name: String(item.name ?? fallback.name),
      status: String(item.status ?? fallback.status),
      oil: Number(item.oil_bopd ?? fallback.oil),
      temp: Number(item.temperature_c ?? fallback.temp),
      pressure: Number(item.pressure_bar ?? fallback.pressure),
      viscosity: Number(item.viscosity_cp ?? fallback.viscosity),
      spm: Number(item.spm ?? fallback.spm),
      stroke: Number(item.stroke_in ?? fallback.stroke),
      vfd: Number(item.vfd_hz ?? fallback.vfd),
      steam: Number(item.steam_ton ?? fallback.steam),
      sor: Number(item.sor ?? fallback.sor),
      efficiency: Number(item.pump_efficiency ?? fallback.efficiency),
      risk: String(item.risk ?? fallback.risk) as Well['risk'],
    }
  })
}

export type Alert = { id: number; severity: string; well: string; time: string; title: string; detail: string; action: string; status: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED' }
export const initialAlerts: Alert[] = [
  { id: 1, severity: 'critical', well: 'BGL-014', time: '08:42', title: 'Rod floating signature detected', detail: 'Pump fillage 54% with cyclic load variance +18%.', action: 'Reduce speed to 6.8 SPM; verify fluid level and review dynamometer card.', status: 'OPEN' },
  { id: 2, severity: 'high', well: 'BGL-005', time: '08:16', title: 'Elevated rod load', detail: 'Peak load 36.2 kN, 12% above the 24-hour baseline.', action: 'Inspect rod string and review VFD ramp profile.', status: 'OPEN' },
  { id: 3, severity: 'medium', well: 'BGL-012', time: '07:58', title: 'Viscosity approaching operating limit', detail: 'Estimated viscosity 1,940 cP at 50°C reservoir temperature.', action: 'Review next CSS timing and check recent temperature trend.', status: 'ACKNOWLEDGED' },
  { id: 4, severity: 'medium', well: 'BGL-019', time: '07:31', title: 'SOR above area median', detail: 'Current cycle SOR 4.9 vs area median 3.8.', action: 'Review steam allocation and production cut-off.', status: 'OPEN' },
  { id: 5, severity: 'low', well: 'BGL-008', time: '06:50', title: 'Production decline watch', detail: '7-day oil rate trend is down 6.2%.', action: 'Compare fluid level and pump fillage before intervention.', status: 'RESOLVED' },
]

export const productionSeries = Array.from({ length: 30 }, (_, i) => {
  const day = i + 1
  const actual = Math.round(1830 + Math.sin(i / 4) * 55 - i * 1.1 + (i > 19 ? 75 : 0))
  return { day: `${day}`, actual, forecast: day > 21 ? Math.round(actual + (day - 21) * 4.2) : null, optimized: day > 21 ? Math.round(actual + 60 + (day - 21) * 6) : null }
})
export const temperatureSeries = Array.from({ length: 18 }, (_, i) => ({
  week: `W${i + 1}`, actual: i < 11 ? Math.round(72 - i * 1.6) : null,
  predicted: i >= 9 ? Math.round(72 - i * 1.6) : null,
  threshold: 52,
}))
export const trendSeries = Array.from({ length: 12 }, (_, i) => ({
  month: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'][i],
  oil: Math.round(2040 - i * 17 + Math.sin(i) * 32), steam: 6900 + i * 70,
  viscosity: 1020 + i * 29, temp: 64 - i * 1.4,
}))

export const roleLabel: Record<string, string> = { ADMIN: 'Administrator', OPERATIONS_MANAGER: 'Operations manager', FIELD_ENGINEER: 'Field engineer' }
