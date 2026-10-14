"""Approval gates, action budgets, and sensitive action heuristics."""
from dataclasses import dataclass
from urllib.parse import urlparse
from .security import PolicyError

DANGEROUS_TERMS=('purchase','buy now','checkout','delete','remove account','send','submit payment','transfer','publish','confirm order','unsubscribe')
@dataclass(frozen=True)
class ActionPolicy:
    allow_interactions: bool=False
    allow_sensitive: bool=False
    max_actions: int=50
    def check(self,action,observation,used=0):
        if used>=self.max_actions: raise PolicyError('Action budget exceeded')
        if action.kind in ('click','fill','press','select','upload') and not self.allow_interactions:
            raise PolicyError('Interactive action requires explicit permission')
        descriptor=' '.join(str(x or '') for x in (action.selector,action.reason,action.value)).lower()
        if any(term in descriptor for term in DANGEROUS_TERMS) and not self.allow_sensitive:
            raise PolicyError('Potentially sensitive action requires separate approval')
        if action.kind=='upload' and not self.allow_sensitive:
            raise PolicyError('File uploads require separate approval')
