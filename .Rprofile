## R 启动配置文件
## 用于 MUC-QMJH 数据分析项目

# 设置 CRAN 镜像（加速包下载）
options(repos = c(CRAN = "https://cloud.r-project.org/"))

# 设置默认编码为 UTF-8
options(encoding = "UTF-8")

# radian 特定配置
if (interactive() && Sys.getenv("RSTUDIO") == "") {
  # 仅在交互式会话中执行，且不在 RStudio 中
  if (require("httpgd", quietly = TRUE)) {
    # 若已安装 httpgd，尝试启用它以获得更好的绘图体验
    options(vsc.plot = TRUE)
  }
}

# 设置工作目录提示（可选，便于调试）
.First <- function() {
  cat("================================================================================\n")
  cat("R", getRversion()$major, ".", getRversion()$minor, "\n")
  cat("Working directory:", getwd(), "\n")
  cat("================================================================================\n")
}，，

# 关闭蜜蜂声（可选）
options(warning.length = 100L)
