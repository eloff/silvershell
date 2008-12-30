all_feature_names = [
    "nested_scopes",
    "generators",
    "division",
    "absolute_import",
    "with_statement",
]

__all__ = ["all_feature_names"] + all_feature_names

g = globals()
for name in all_feature_names:
	g[name] = True
