# tool-ghcr-docker-packager

> **Docker Buildx 多架构打包、GHCR 容器发布与 Sigstore/Cosign 签名编排器**  
> Universal CLI Facade (UCFS v1.0) 标准实现 | 100% 离线自省 | 多架构交叉构建 (AMD64 & ARM64) 与 OIDC 密码学签名

---

## 🌟 核心价值与实用性痛点解答

在将微服务与智能体系统容器化并分发到 GitHub Container Registry (ghcr.io) 时，传统手动构建面临诸多困境：
1. **单一架构架构误区**：在 x86 电脑上默认打包只生成 `linux/amd64` 镜像，当下游在 Apple Silicon (M1/M2/M3) 或 ARM 云服务器（如 AWS Graviton、华为鲲鹏）运行时，直接报 `exec format error` 崩溃。
2. **供应链投毒与溯源缺失**：未对镜像进行数字签名，镜像在拉取时无法验证是否被中间人篡改或恶意替换。
3. **工作流配置繁琐**：配置 QEMU 跨架构仿真、Buildx 实例缓存、GitHub OIDC 无密钥凭证以及 Cosign 签名流水线往往需要数十次 CI 调试。

`tool-ghcr-docker-packager` 封装了全套现代化容器分发流水线：
- **多架构自动化声明**：原生支持 `linux/amd64` 与 `linux/arm64` 双平台并行构建。
- **Sigstore/Cosign 无秘钥签名方案**：利用 GitHub Actions OIDC 身份自动签名并附加 SBOM 凭据，符合 SLSA 级别供应链安全。
- **一键生成发布工作流 (`.github/workflows/ghcr-publish.yml`)**：在 Git Tag 推送时自动构建、推送到 `ghcr.io` 并执行签名。

---

## ⚡ 极速开始 (Quick Start in 3 Seconds)

```bash
# 1. 环境校验
python main.py setup

# 2. 对当前项目生成多架构构建指令与发布流水线
python main.py run

# 3. 运行离线单元测试
python main.py test

# 4. 核心健康自检
python main.py health

# 5. 清理缓存
python main.py clean
```

### 高级功能：定制构建与签名规划
```bash
# 生成并审查指定服务的多架构 Buildx 指令与 Cosign 签名计划
python main.py build --target D:\github\my-service --owner my-org --tags "v1.0.0,latest"

# 针对已有镜像生成 Cosign 签名与 SBOM 溯源凭证附加指令
python main.py sign --image ghcr.io/my-org/my-service:v1.0.0 --sbom sbom.spdx.json
```

---

## 🛡️ 架构与不变式

- **独立职责**：专注 Docker Buildx 多架构参数与 GHCR/Cosign 工作流编排，不常驻容器守护进程。
- **离线确定性**：无本地 Docker 引擎或网络时，自动以沙箱仿真模式生成准确命令与工作流。

---

## 🚫 Non-Goals (明确非目标)

1. **不替代 Docker 守护进程**：镜像的实际层构建由本地 Docker Engine 或 GitHub Actions Ubuntu Runner 执行。
2. **不存储明文凭证**：遵循 OIDC 无密钥安全标准，绝不落盘或硬编码 Docker 登录密码。
3. **不修改用户 Dockerfile**：本工具仅校验语法与构建参数，不擅自修改用户 Dockerfile 逻辑。
