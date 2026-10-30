# wardlab-board

[wardlab.io](https://wardlab.io/) 公共看板的发布仓库。

- 网站内容在 `gh-pages` 分支：wardlab 服务约每 15 分钟生成一次并推送，每次是一个没有历史的新提交。
- `main` 分支只放停更检查：GitHub Actions 每小时读取一次 https://wardlab.io/board/ 的生成时间和报价时间，超过 2 小时没有更新就让检查失败，由 GitHub 通知维护者；持续停更时每 6 小时再提醒一次。

This repository publishes [wardlab.io](https://wardlab.io/). The site lives on the `gh-pages` branch, regenerated about every 15 minutes. The `main` branch holds only an hourly freshness check that fails, and so notifies the maintainer, when the site has not been updated for 2 hours.
