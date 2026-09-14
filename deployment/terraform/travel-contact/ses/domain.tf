# SES Domain Identity
resource "aws_ses_domain_identity" "main" {
  provider = aws.singapore
  domain   = var.ses_domain
}

# SES Domain DKIM
resource "aws_ses_domain_dkim" "main" {
  provider = aws.singapore
  domain   = aws_ses_domain_identity.main.domain
}

# SES Domain Mail From
resource "aws_ses_domain_mail_from" "main" {
  provider         = aws.singapore
  count            = var.ses_domain != "" ? 1 : 0
  domain           = aws_ses_domain_identity.main.domain
  mail_from_domain = "mail.${var.ses_domain}"
}
