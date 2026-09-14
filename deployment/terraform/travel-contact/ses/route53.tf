# SES Verified Domain SPF Record
resource "aws_route53_record" "ses_spf" {
  count = var.create_route53_records ? 1 : 0

  zone_id = var.route53_zone_id
  name    = var.ses_domain
  type    = "TXT"
  ttl     = 300
  records = [
    "v=spf1 include:amazonses.com ~all"
  ]
}

# SES DKIM Route53 Records
resource "aws_route53_record" "ses_dkim" {
  count = var.create_route53_records ? length(aws_ses_domain_dkim.main.dkim_tokens) : 0

  zone_id = var.route53_zone_id
  name    = "${element(aws_ses_domain_dkim.main.dkim_tokens, count.index)}._domainkey.${var.ses_domain}"
  type    = "CNAME"
  ttl     = 300
  records = [
    "${element(aws_ses_domain_dkim.main.dkim_tokens, count.index)}.dkim.amazonses.com"
  ]
}

# SES Mail From Route53 MX Record
resource "aws_route53_record" "ses_mail_from" {
  count = var.create_route53_records ? 1 : 0

  zone_id = var.route53_zone_id
  name    = "bounce.${var.ses_domain}"
  type    = "MX"
  ttl     = 300
  records = [
    "10 feedback-smtp.${var.singapore_region}.amazonses.com"
  ]
}

# SES Mail From SPF Record
resource "aws_route53_record" "ses_mail_from_spf" {
  count = var.create_route53_records ? 1 : 0

  zone_id = var.route53_zone_id
  name    = "bounce.${var.ses_domain}"
  type    = "TXT"
  ttl     = 300
  records = [
    "v=spf1 include:amazonses.com ~all"
  ]
}
