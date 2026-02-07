# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Login page adds dual mode: WeChat login and account login (`username/phone/email + password`).
- Login page adds direct entry to email-code registration.
- Backend supports nickname (username) as account credential during password login.
- Added username uniqueness checks in register and profile update flows.
- `.env.example` adds WeChat and SMTP related config examples.

### Changed
- WeChat login now requires real user profile authorization; rejects non-authorized login attempts.
- Existing WeChat users now refresh nickname and avatar on each authorized login.
- Disabled WeChat dev fallback by default (`ALLOW_WECHAT_LOGIN_WITHOUT_SECRET=false`).
- Improved email-code send error response to expose concrete backend failure message.
- Home strategy cards now use deterministic sequence numbers to avoid duplicate labels.

### Fixed
- Fixed garbled arrow text in user menu (`>` rendering issue in mini program view).
- Fixed button text vertical alignment issue for user logout and login action buttons.
- Fixed partial garbled comments/text fragments in homepage style section.
