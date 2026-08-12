import { apiGet, apiPost } from './client.js'

export function getProject(projectName) {
  return apiGet(`/project/${projectName}`)
}

export function getSummary(projectName) {
  return apiGet(`/project/${projectName}/summary`)
}

export function getMaterial(projectName, materialId) {
  return apiGet(`/project/${projectName}/material/${materialId}`)
}

export function listProjects() {
  return apiGet(`/project/list`)
}

export function runWhatIf(projectName, changes) {
  return apiPost(`/project/${projectName}/whatif`, {
    project_name: projectName,
    changes,
  })
}

export function buildProject(projectInput) {
  return apiPost(`/project/build`, projectInput)
}

export function getVendors(projectName) {
  return apiGet(`/project/${projectName}/vendors`)
}