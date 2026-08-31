# SES Sender Email Identity
resource "aws_ses_email_identity" "sender" {
  provider = aws.singapore
  count    = var.ses_source_email != "" ? 1 : 0
  email    = var.ses_source_email
}

# SES Recipient Email Identity
resource "aws_ses_email_identity" "recipient" {
  provider = aws.singapore
  count    = var.ses_destination_email != "" ? 1 : 0
  email    = var.ses_destination_email
}