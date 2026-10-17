variable "name" { type = string }
variable "bucket_arn" { type = string }
variable "tags" { type = map(string) }
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_iam_policy_document" "glue_assume" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:glue:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"]
    }
  }
}
resource "aws_iam_role" "glue" {
  name = "${var.name}-glue"
  assume_role_policy = data.aws_iam_policy_document.glue_assume.json
  tags = var.tags
}
data "aws_iam_policy_document" "glue_data" {
  statement {
    sid       = "ListDataLake"
    actions   = ["s3:ListBucket"]
    resources = [var.bucket_arn]
  }
  statement {
    sid       = "ReadWriteDataLake"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${var.bucket_arn}/*"]
  }
}
resource "aws_iam_role_policy" "glue_data" {
  name = "data-lake-access"
  role = aws_iam_role.glue.id
  policy = data.aws_iam_policy_document.glue_data.json
}
resource "aws_iam_role_policy_attachment" "glue_service" {
  role = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}
output "glue_role_arn" { value = aws_iam_role.glue.arn }
