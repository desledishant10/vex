"""Provider implementations — talk to actual model APIs.

Providers translate Vex's provider-agnostic :class:`Conversation` and
:class:`Message` into the native schema of each model API. Each provider
implements :meth:`Provider.complete`, which returns ``(text, raw_response)``.

Concrete providers live next to this module; optional dependencies are guarded
so installing one provider doesn't pull all SDKs.
"""

from vex.providers.base import Provider

__all__ = ["Provider"]
