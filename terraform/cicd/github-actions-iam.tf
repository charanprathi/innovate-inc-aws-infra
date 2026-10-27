resource "aws_iam_user" "github_actions" {
  name = "innovate-inc-github-actions"
}

resource "aws_iam_policy" "ecr_push_pull" {
  name        = "innovate-inc-ecr-push-pull"
  description = "Allows GitHub Actions to push/pull images to ECR repos for this project"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECRAuth"
        Effect = "Allow"
        Action = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Sid    = "ECRPushPull"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = [
          aws_ecr_repository.app["dev"].arn,
          aws_ecr_repository.app["staging"].arn,
          aws_ecr_repository.app["prod"].arn
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "github_actions_ecr" {
  user       = aws_iam_user.github_actions.name
  policy_arn = aws_iam_policy.ecr_push_pull.arn
}

resource "aws_iam_access_key" "github_actions" {
  user = aws_iam_user.github_actions.name
}

output "github_actions_access_key_id" {
  value = aws_iam_access_key.github_actions.id
}

output "github_actions_secret_access_key" {
  value     = aws_iam_access_key.github_actions.secret
  sensitive = true
}
