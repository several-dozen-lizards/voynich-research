"""C3 structural guards only. This module has no scientific/vault executor."""
class NotAdmitted(ValueError):pass

def retain_geometry_slots(slots,reading):
 """Missing labels stay None in the fixed physical slots; never compact by readability."""
 ids=[s['slot_id'] for s in slots]
 if not slots or len(set(ids))!=len(ids):raise NotAdmitted('unique physical slots required')
 if any(s.get('folio') in {'f72v1','f72v2','f73r','f73v'} for s in slots):raise NotAdmitted('reserved material forbidden in open preflight')
 return [(s['slot_id'],s.get('labels',{}).get(reading)) for s in slots]

def literal_count_compatibility(list_size,slots):
 if type(list_size) is not int or list_size<=0:raise NotAdmitted('declared complete list size required')
 if len(slots)!=list_size:raise NotAdmitted('complete list and physical geometry length differ; no truncation/padding/readable compression')
 return True

def role_pair(source_codes):
 if source_codes!={'H':'H','R2':'K'}:raise NotAdmitted('v7.3 frozen label roles are H and K; no fallback by outcome')
 return True

def scientific_release(*args,**kwargs):
 # Deliberately cannot be enabled with a caller-supplied admission/approval boolean.
 raise NotAdmitted('No admitted C3 registration/model/null-qualification packet. Scientific and vault routes remain absent.')
