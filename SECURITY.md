# Security Policy
This document outlines the security practices and guidelines for maintaining the security of this application.
It provides information on how security vulnerabilities are addressed, and it's reporting procedures.

## Scope
This security policy applies to all parts of `PingTool`, including the codebase, server and client implementation. \
Dependencies used by PingTool are not covered by this policy.

### Supported releases
All versions of `PingTool` are supported.

### Supported environments
Patches do not take into account the environment PingTool is running on. \
However, outdated or unreasonable environments may not be supported, use your common sense!

Some rules of thumb;
- **Unsupported Operating Systems:** Using `PingTool` on operating systems that have reached their end-of-life 
or are no longer receiving security updates could be considered `outdated`.
- **Outdated Dependencies:** If the dependencies you have installed are outdated and no longer receive 
updates or support, it may be considered an unreasonable `environment`.
**Note:** This does not apply to dependencies specified by `PingTool` itself.
- **Obsolete Hardware:** Running `PingTool` on hardware that is technologically obsolete and no longer supported by the 
manufacturer could be considered `outdated` and `unreasonable`.

## Reporting Security Issues
To report a security vulnerability, create an issue in the 
[repository](https://github.com/DeadlyFirex/PingTool). \
Please follow these steps:

- Assign the issue to `@DeadlyFirex`.
- Apply appropriate labels, especially the "vulnerability" label to the issue.
- Mention `@DeadlyFirex` within the issue description or comments.

### Handling of issues
Upon reporting a vulnerability:

- The issue will be addressed and fixed within 48 hours, and you'll be notified of its status.
- Please do not share any information (publicly) about the vulnerability before it's resolved.

I appreciate responsible disclosure and cooperation in maintaining security of opensource software. 
For any urgent security concerns, reach out directly!
