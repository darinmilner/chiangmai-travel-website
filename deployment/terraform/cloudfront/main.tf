# NEW: Define Origin Access Control
resource "aws_cloudfront_origin_access_control" "oac" {
  name                              = "${local.lower_app_name}-s3-oac"
  description                       = "OAC for ${aws_s3_bucket.static_bucket.id}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "images" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases             = var.custom_domains
  price_class         = var.price_class

  origin {
    domain_name = aws_s3_bucket.static_bucket.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.static_bucket.id}"

    # NEW: Attach OAC ID directly to the origin
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
  }

  default_cache_behavior {
    target_origin_id       = "S3Origin"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD", "OPTIONS"]

    cache_policy_id            = aws_cloudfront_cache_policy.images.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    min_ttl     = var.min_ttl
    default_ttl = var.default_ttl
    max_ttl     = var.max_ttl
  }

  # Custom cache behavior for images
  ordered_cache_behavior {
    path_pattern           = "/${var.s3_prefix}/*.jpg"
    target_origin_id       = "S3Origin"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD", "OPTIONS"]

    cache_policy_id            = aws_cloudfront_cache_policy.images.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    min_ttl     = var.min_ttl
    default_ttl = var.default_ttl
    max_ttl     = var.max_ttl
  }

  # Cache behavior for WebP images
  ordered_cache_behavior {
    path_pattern           = "/${var.s3_prefix}/*.webp"
    target_origin_id       = "S3Origin"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    cached_methods  = ["GET", "HEAD", "OPTIONS"]

    cache_policy_id            = aws_cloudfront_cache_policy.images.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id

    min_ttl     = var.min_ttl
    default_ttl = var.default_ttl
    max_ttl     = var.max_ttl
  }

  restrictions {
    geo_restriction {
      restriction_type = var.geo_restriction_type
      locations        = var.geo_restriction_locations
    }
  }

  viewer_certificate {
    # If ARN is null, use default certificate
    cloudfront_default_certificate = var.certificate_arn == null ? true : false

    # If ARN is provided, use ACM certificate
    acm_certificate_arn      = var.certificate_arn
    ssl_support_method       = var.certificate_arn != null ? "sni-only" : null
    minimum_protocol_version = var.certificate_arn != null ? "TLSv1.2_2021" : "TLSv1"
  }

  custom_error_response {
    error_caching_min_ttl = 300
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
  }

  tags = local.common_tags
}

# CloudFront Cache Policy
resource "aws_cloudfront_cache_policy" "images" {
  name        = "${local.lower_app_name}-image-cache"
  comment     = "Cache policy for villa images"
  default_ttl = var.default_ttl
  max_ttl     = var.max_ttl
  min_ttl     = var.min_ttl

  parameters_in_cache_key_and_forwarded_to_origin {
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true

    headers_config {
      header_behavior = "none"
    }

    cookies_config {
      cookie_behavior = "none"
    }

    query_strings_config {
      query_string_behavior = "none"
    }
  }
}

resource "aws_cloudfront_response_headers_policy" "security" {
  name    = "${local.lower_app_name}-security-headers"
  comment = "Security and CORS headers for images"

  security_headers_config {
    content_type_options {
      override = true
    }

    frame_options {
      frame_option = "DENY"
      override     = true
    }

    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }

    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = true
      override                   = true
    }

    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
  }

  cors_config {
    # REQUIRED: Must be set to false when using wildcard origins ("*")
    access_control_allow_credentials = false

    access_control_allow_origins {
      items = ["*"] # Replace with ["https://yourdomain.com"] for stricter security
    }
    access_control_allow_headers {
      items = ["*"]
    }
    access_control_allow_methods {
      items = ["GET", "HEAD", "OPTIONS"]
    }
    access_control_expose_headers {
      items = ["ETag"]
    }
    access_control_max_age_sec = 3000
    origin_override            = true
  }
}
