# QuIP 1: Qrexec policy API

This is Qubes Improvement Proposal 1, *draft 20180221*.

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

Currently only administrator API is defined and implemented. The operator API
will be done in second phase.

## Proposed qrexec RPC calls

notation convention: `rpcname+argument(payload) → dst`

### administrator API

- `policy.Get+RPCNAME (ARGUMENT) → dom0`
  Get the contents of the policy.
- `policy.Remove+RPCNAME (ARGUMENT) → dom0`
  Remove the policy by `unlink()`ing the respective file. After this call, the
  default policy is in force (user will be asked to create a file).
- `policy.List () → dom0`
  List all policy files with their arguments.
- `policy.List+RPCNAME () → dom0`
  List policy files for a particular call (in practice, this yields a list of
  known arguments).
- `policy.Replace+RPCNAME (see below) → dom0`
  Replace the entire policy. The payload is argument specification and then
  the content. Argument specification is either one octet specifying argument
  length following the actual argument (Pascal-style string of length 0-254), or
  `0xFF` which means that there is no argument. This is to make distinction
  between no argument at all (which will replace default file for whole
  `RPCNAME`) and an empty argument, which is nonetheless present.

- `policy.include.Get+FILENAME () → dom0`
  Get the contents of policy include file. FILENAME is inside
  `/etc/qubes-rpc/policy/include` directory.
- `policy.include.Replace+FILENAME (new policy) → dom0`
  Replace the entire contents of policy include file.
- `policy.include.Remove+FILENAME () → dom0`
  Unlink() the file.
- `policy.include.List () → dom0`
  List all available files.

## Varia

- By default all calls are prohibited. The owner has to establish initial policy
  by external means. *(Will it be true for the install with guiqube?)*

- There is very real possibility of shooting oneself in the foot, especially
  with administrator API. The API endpoints do not attempt to prevent that, by
  client tools may for example forbid operating on RPCNAMEs `policy.*`. However,
  syntax may be checked.

<!-- vim: set tw=80 ts=2 sts=2 sw=2 et : -->
