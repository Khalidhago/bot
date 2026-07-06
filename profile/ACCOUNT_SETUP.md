# Sorting your GitHub account — 15-minute checklist

These are the account-level changes that make a profile read as senior and
professional. They must be done while logged in at github.com (an API token
scoped to a repository cannot change profile settings), so each step below
is a manual click-through — none takes more than a minute.

## 1. Profile settings — https://github.com/settings/profile

| Field | Current | Set it to |
| --- | --- | --- |
| Name | `khalid hago` | `Khalid Hago` (capitalised) |
| Bio | (empty) | `Drone systems consultant — PX4/ArduPilot, ROS 2, and UAV hardware. Founder @ Hago Drone Consulting Services.` |
| Company | `Hago Drone Consulting Services` | ✅ already good |
| Location | (empty) | your city/country — recruiters and clients filter by it |
| Website | (empty) | company site or LinkedIn |
| Profile photo | default? | a clear headshot, or a clean company logo |

## 2. Profile README (the big banner on your profile)

1. Create a new **public** repository named exactly `Khalidhago`
   (Repositories → New; GitHub will note it's a special repository).
2. Initialise it with a README and replace the content with
   [`profile/README.md`](README.md) from this repo.
3. Fill in every `[bracketed]` placeholder — delete lines that don't apply.
   Don't state experience or credentials you can't back up; link to work
   instead.

## 3. Pin your best work — on https://github.com/Khalidhago

Click **Customize your pins** and pin `bot` (and future project repos).
Pinned repos with real READMEs and green CI are what visitors judge first.

## 4. Repository presentation — https://github.com/Khalidhago/bot

- **About box** (gear icon, right side): description
  `ROS 2 robotics stack — ground rover + UAV telemetry, phone teleop, SLAM/Nav2`
  and topics: `ros2`, `robotics`, `drone`, `uav`, `mavlink`, `px4`, `nav2`,
  `slam`, `teleoperation`.
- **Default branch**: rename `claude/ros-mobile-system-zmaz54` → `main`
  (Settings → Branches → pencil icon). GitHub redirects old links
  automatically.

## 5. Account hygiene — https://github.com/settings

- **Security**: enable two-factor authentication (Settings → Password and
  authentication). Serious accounts have the 2FA requirement met.
- **Emails**: decide whether your email is public (Settings → Emails →
  "Keep my email addresses private" if not).
- **Following list**: you follow 41 accounts — no need to change, but
  following active robotics/UAV orgs (PX4, ArduPilot, ROS) keeps your feed
  and public activity on-topic.

## 6. Ongoing habits (what actually reads as "senior")

- Commit regularly with clear messages — the contribution graph is checked.
- Every public repo gets a real README, a license, and CI, or stays private.
- Write one short `docs/` note per project on a design decision — this
  demonstrates judgement, which is the thing seniority actually signals.
