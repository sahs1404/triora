/**
 * Converts parsed CSV rows (from papaparse) into the ProjectInput shape
 * expected by POST /project/build. Mirrors the logic in
 * backend/csv_to_json_test.py — keep both in sync if the schema changes.
 */

export function buildProjectInput(projectName, activityRows, materialRows, vendorRows) {
  const activities = activityRows.map((row) => ({
    id: row.id?.trim(),
    name: row.name?.trim(),
    duration_days: parseInt(row.duration_days, 10),
    predecessors: row.predecessors ? row.predecessors.split('|').map((p) => p.trim()) : [],
  }))

  const vendors = vendorRows.map((row) => ({
    id: row.id?.trim(),
    name: row.name?.trim(),
    historical_delay_rate: parseFloat(row.historical_delay_rate),
    jobs_completed: parseInt(row.jobs_completed, 10) || 0,
    jobs_delayed: parseInt(row.jobs_delayed, 10) || 0,
  }))

  const materials = materialRows.map((row) => ({
    id: row.id?.trim(),
    name: row.name?.trim(),
    activity_id: row.activity_id?.trim(),
    vendor_id: row.vendor_id?.trim() || null,
    lead_time_days: parseInt(row.lead_time_days, 10),
    promised_delivery_date: row.promised_delivery_date?.trim() || null,
    need_by_date: row.need_by_date?.trim() || null,
    vendor_reported_status: row.vendor_reported_status?.trim() || null,
    manual_p_delay_override:
      row.manual_p_delay_override && row.manual_p_delay_override.trim() !== ''
        ? parseFloat(row.manual_p_delay_override)
        : null,
  }))

  return {
    project_name: projectName,
    activities,
    materials,
    vendors,
  }
}