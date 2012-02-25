${str(o.outcome)}
%if o.rich_data["in-debian"]:
%if o.rich_data["nmu"]:
- Detected as a non-maintainer upload
%endif
- The package uploader is ${"not" if not o.rich_data["is-debian-maintainer"] else ""} currently maintaining ${o.package_version.package.name} in Debian
%endif
