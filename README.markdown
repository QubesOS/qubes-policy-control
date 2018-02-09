# QuIP 1: Qrexec policy API

This is Qubes Improvement Proposal 1, *draft 20180209*.

## Statement of the problem

If a user that is not fully trusted is allowed to manage a subset of qubes, the
user should also have the possibility to set a policy for those qubes. For
example, user should have the possibility to explicitly allow or deny the
availability of cryptographic services, like split gpg or U2F. The problem is,
those services may not be known at the time of setting master policy, so there
is no possibility to create a set of tags to be wielded by the user.

Another problem is that some of the services are exposed by "shared" qubes like
`sys-usb` for U2F tokens or `sys-net` for access to network to perform upgrades.

An API is provided to allow changing of the underlying qrexec policy. API is
divided into two sections: administrator API and operator API. Administrator API
exposes full functionality and is used to restore backups, but itself cannot be
policed with fine-grained controls. Operator API does not allow for all possible
combinations, but can be exposed to less trusted users with precise policy.

## Proposed qrexec RPC calls

notation convention: `rpcname+argument(payload) → dst`

### administrator API

- `policy.Get+RPCNAME[+ARGUMENT] () → dom0`
  Get the contents of the policy.
- `policy.Replace+RPCNAME[+ARGUMENT] (new policy) → dom0`
  Replace the entire policy.
- `policy.Remove+RPCNAME[+ARGUMENT] () → dom0`
  Remove the policy by unlink()ing the respective file. After this call, the
  default policy is in force (user will be asked to create a file).
- `policy.List () → dom0`
  List all policy files with their arguments.
- `policy.List+RPCNAME () → dom0`
  List policy files for a particular call (in practice, this yields a list of
  known arguments).

- `policy.include.Get+FILENAME () → dom0`
  Get the contents of policy include file.
- `policy.include.Replace+FILENAME (new policy) → dom0`
  Replace the entire contents of policy include file.
- `policy.include.Remove+FILENAME () → dom0`
  Unlink() the file.
- `policy.include.List () → dom0`
  List all available files.

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

## Varia

- By default all calls are prohibited. The owner has to establish initial policy
  by external means. *(Will it be true for the install with guiqube?)*

- There is very real possibility of shooting oneself in the foot, especially
  with administrator API. The API endpoints do not attempt to prevent that, by
  client tools may for example forbid operating on RPCNAMEs `policy.*`. However,
  syntax may be checked.

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
