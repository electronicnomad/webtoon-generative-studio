output "promptlandia_url" {
  description = "The URL of the deployed Promptlandia service."
  value       = google_cloud_run_v2_service.promptlandia_service.uri
}
