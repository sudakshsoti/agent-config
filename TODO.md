# TODO

- [ ] Fix the Pi Plan Build stale-context crash (paused at user request).
  - Installed package: `@janvitos/pi-plan-build` version `0.1.59` in `~/.pi/agent/npm/node_modules/`.
  - Reported error: `This extension ctx is stale after session replacement or reload`.
  - Stack points to `index.ts:132` (`formatRail` accessing `currentContext.ui.theme`) through `user-message-rail.ts:163` (`renderWithModeRail`).
  - Investigation only: no reproduction, fix, or verification completed. Check upstream for an existing fix before patching; reproduce rendering across reload/session replacement and verify the focused fix.
  - Preserve unrelated changes in `pi/extensions/operational-footer/index.js`. Model-ladder changes are separate and have not been approved.
