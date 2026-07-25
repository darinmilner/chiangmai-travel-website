terraform {
  backend "s3" {
    bucket = "chiangmaivilla-backendfiles-apsoutheast7-beta"
    key    = "statefiles/secrets/terraform.tfstate"
    region = "ap-southeast-7"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
