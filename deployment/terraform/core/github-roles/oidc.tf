# GitHub Actions uses OpenID Connect (OIDC) to let your workflow authenticate directly to AWS using a short-lived token.
# To trust GitHub as an identity source, AWS needs an OIDC provider resource:
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]

  thumbprint_list = [
    # GitHub’s root CA thumbprint — updated if GitHub changes its certificate
    "6938fd4d98bab03faadb97b34396831e3780aea1"
  ]
}
