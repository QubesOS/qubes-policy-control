# DRAFT

This is unfinished API which would allow more granular policing, so it could be
exposed to less trusted users.

### operator API

Those calls add appropriate rules at the top of the file. No rule is replaced,
just the new one is added. If there is `$endpreamble` directive in the file,
insert after that one instead. This allows to specify preamble with overriding
policy by the administrator.

- `policy.Allow+DSTQUBE+RPCNAME[+ARGUMENT] () → SRCQUBE`
    `SRCQUBE DSTQUBE allow`
- `policy.AllowWithTarget+DSTQUBE+TARGET+RPCNAME[+ARGUMENT] () → SRCQUBE`
- `policy.AllowTag+TAGNAME+RPCNAME[+ARGUMENT] () → SRCQUBE`
- `policy.AllowDefaultWithTarget+DSTQUBE+RPCNAME[+ARGUMENT] () → SRCQUBE`
    `SRCQUBE $default allow,target=DSTQUBE`

- `policy.Ask+DSTQUBE+RPCNAME[+ARGUMENT] () → SRCQUBE`
    `SRCQUBE DSTQUBE ask`
- `policy.AskWithDefault+DSTQUBE+RPCNAME[+ARGUMENT] (DEFAULT) → SRCQUBE`
    `SRCQUBE DSTQUBE ask,default_target=DEFAULT` i sprawdza, czy taki default
    faktycznie da się wybrać

- `policy.Deny+DSTQUBE+RPCNAME[+ARGUMENT] () → SRCQUBE`
- `policy.DenyDefault+RPCNAME[+ARGUMENT] () → SRCQUBE`
- `policy.DenyTag+TAGNAME+RPCNAME[+ARGUMENT] () → SRCQUBE`

- `policy.RequestArgument+RPCNAME (ARGUMENT) → VM`: Add a rule which allows VM
  to call originating qube with RPCNAME+ARGUMENT.

`(SRCQUBE == dom0) => src=$any`

*TODO* tag for src?

## Proposed changes to qrexec

- Maximum qrexec RPC name length should be set at 256 octets. Rationale:
  `len('policy.AllowDefaultWithTarget+testvm1+admin.pool.volume.Set.revisions_to_keep') == 77`

## Proposed changes to policy syntax

- `$include:FILENAME` references `/etc/qubes-rpc/policy/include/FILENAME`.
  Rationale: consistency with API (FILENAME==FILENAME). If file is not found,
  falls back to old behaviour. Old behaviour deprecated in R4.1, removed in R5.0
  (or 5.0/6.0). During deprecation backup should rewrite the file for future
  compatibility (restore-time workaround is not needed, since there are no
  official backup yet).

- New directive `$end-preamble` (as the only token in the line) is ignored, but
  relevant to the operator API. Rationale: see operator API.

- New directive `$eval-on-redirect` (as the only token in the line) causes the
  policy to be evaluated again when `allow,target=...` rule is in effect. If the
  resulting call is not allowed by any unqualified `allow` or `ask`, the request
  is denied. This would cause preamble to be binding, so 

- Alternative: use some other prefix char for directives to distinguish them
  from rule tokens which use `$`. This may be the exclamation mark.
  (`!end-preamble`, `!eval-on-redirect`, `!include:FILENAME`).

- Option: rename tokens. Old token remains as deprecated aliases with no
  timeline for removal (alternative: specify timeline). Rationale: deprecate
  "vm" terminology in favour of "qube" and possible Odyssey actualisation. This
  change is not needed, but if deemed OK, should be applied within same release
  cycle to consolidate breaking changes.

  - `$anyvm` to `$any`
  - `$adminvm` to `$admin`
  - `dom0` to `$admin`

<!-- vim: set tw=80 ts=2 sts=2 sw=2 et : -->
