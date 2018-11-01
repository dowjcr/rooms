# === AUTO-GENERATED - DO NOT EDIT ===

# --------------------------------------------------------------------------
# Copyright (c) 2012, University of Cambridge Computing Service
#
# This file is part of the Lookup/Ibis client library.
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------

"""
Web service API methods. This module is fully auto-generated, and contains
the Python equivalent of the `XxxMethods` Java classes for executing all API
methods.
"""

from .connection import IbisException

class IbisMethods:
    """
    Common methods for searching for objects in the Lookup/Ibis database.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    def __init__(self, conn):
        self.conn = conn

    def getVersion(self):
        """
        Get the current API version number.

        ``[ HTTP: GET /api/v1/version ]``

        **Returns**
          str
            The API version number string.
        """
        path = "api/v1/version"
        path_params = {}
        query_params = {}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.value

class GroupMethods:
    """
    Methods for querying and manipulating groups.

    **The fetch parameter for groups**

    All methods that return groups also accept an optional `fetch`
    parameter that may be used to request additional information about the
    groups returned. For more details about the general rules that apply to
    the `fetch` parameter, refer to the :any:`PersonMethods`
    documentation.

    For groups the `fetch` parameter may be used to fetch references
    to people, institutions or other groups. In each case, only non-cancelled
    people, institutions and groups will be included when fetching references.
    The following references are supported:

    * ``"all_members"`` - fetches all the people who are members of the
      group, including members of groups included by the group, and groups
      included by those groups, and so on.

    * ``"direct_members"`` - fetches all the poeple who are direct
      members of the group, not taking into account any included groups.

    * ``"members_of_inst"`` - if the group is a membership group for an
      institution, this fetches that institution.

    * ``"owning_insts"`` - fetches all the institutions to which the
      group belongs.

    * ``"manages_insts"`` - fetches all the institutions that the group
      manages. Typically this only applies to "Editor" groups.

    * ``"manages_groups"`` - fetches all the groups that this group
      manages. Note that some groups are self-managed, so this may be a
      self-reference.

    * ``"managed_by_groups"`` - fetches all the groups that manage this
      group.

    * ``"reads_groups"`` - fetches all the groups that this group has
      privileged access to. This means that members of this group can see the
      members of the referenced groups regardless of the membership visibility
      settings.

    * ``"read_by_groups"`` - fetches all the groups that have privileged
      access to this group.

    * ``"includes_groups"`` - fetches all the groups included by this
      group.

    * ``"included_by_groups"`` - fetches all the groups that include
      this group.

    As with person `fetch` parameters, the references may be used
    in a chain by using the "dot" notation to fetch additional information
    about referenced people, institutions or groups. For example
    ``"all_members.email"`` will fetch the email addresses of all members
    of the group. For more information about what can be fetched from
    referenced people and institutions, refer to the documentation for
    :any:`PersonMethods` and :any:`InstitutionMethods`.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    def __init__(self, conn):
        self.conn = conn

    def allGroups(self,
                  includeCancelled,
                  fetch=None):
        """
        Return a list of all groups.

        By default, only a few basic details about each group are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references.

        ``[ HTTP: GET /api/v1/group/all-groups ]``

        **Parameters**
          `includeCancelled` : bool
            [optional] Whether or not to include cancelled
            groups. By default, only live groups are returned.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisGroup`
            The requested groups (in groupid order).
        """
        path = "api/v1/group/all-groups"
        path_params = {}
        query_params = {"includeCancelled": includeCancelled,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.groups

    def listGroups(self,
                   groupids,
                   fetch=None):
        """
        Get the groups with the specified IDs or names.

        By default, only a few basic details about each group are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references.

        The results are sorted by groupid.

        .. note::
          The URL path length is limited to around 8000 characters,
          which limits the number of groups that this method can fetch. Group
          IDs are currently 6 characters long, and must be comma separated and
          URL encoded, which limits this method to around 800 groups by ID,
          but probably fewer by name, depending on the group name lengths.

        .. note::
          The groups returned may include cancelled groups. It is the
          caller's repsonsibility to check their cancelled flags.

        ``[ HTTP: GET /api/v1/group/list?groupids=... ]``

        **Parameters**
          `groupids` : str
            [required] A comma-separated list of group IDs or
            group names (may be a mix of both).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisGroup`
            The requested groups (in groupid order).
        """
        path = "api/v1/group/list"
        path_params = {}
        query_params = {"groupids": groupids,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.groups

    def search(self,
               query,
               approxMatches=None,
               includeCancelled=None,
               offset=None,
               limit=None,
               orderBy=None,
               fetch=None):
        """
        Search for groups using a free text query string. This is the same
        search function that is used in the Lookup web application.

        By default, only a few basic details about each group are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references.

        ``[ HTTP: GET /api/v1/group/search?query=... ]``

        **Parameters**
          `query` : str
            [required] The search string.

          `approxMatches` : bool
            [optional] Flag to enable more approximate
            matching in the search, causing more results to be returned. Defaults
            to :any:`False`.

          `includeCancelled` : bool
            [optional] Flag to allow cancelled groups to
            be included. Defaults to :any:`False`.

          `offset` : int
            [optional] The number of results to skip at the start
            of the search. Defaults to 0.

          `limit` : int
            [optional] The maximum number of results to return.
            Defaults to 100.

          `orderBy` : str
            [optional] The order in which to list the results.
            This may be ``"groupid"``, ``"name"`` (the default) or
            ``"title"``.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisGroup`
            The matching groups.
        """
        path = "api/v1/group/search"
        path_params = {}
        query_params = {"query": query,
                        "approxMatches": approxMatches,
                        "includeCancelled": includeCancelled,
                        "offset": offset,
                        "limit": limit,
                        "orderBy": orderBy,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.groups

    def searchCount(self,
                    query,
                    approxMatches=None,
                    includeCancelled=None):
        """
        Count the number of groups that would be returned by a search using
        a free text query string.

        ``[ HTTP: GET /api/v1/group/search-count?query=... ]``

        **Parameters**
          `query` : str
            [required] The search string.

          `approxMatches` : bool
            [optional] Flag to enable more approximate
            matching in the search, causing more results to be returned. Defaults
            to :any:`False`.

          `includeCancelled` : bool
            [optional] Flag to allow cancelled groups to
            be included. Defaults to :any:`False`.

        **Returns**
          int
            The number of matching groups.
        """
        path = "api/v1/group/search-count"
        path_params = {}
        query_params = {"query": query,
                        "approxMatches": approxMatches,
                        "includeCancelled": includeCancelled}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return int(result.value)

    def getGroup(self,
                 groupid,
                 fetch=None):
        """
        Get the group with the specified ID or name.

        By default, only a few basic details about the group are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of the group.

        .. note::
          The group returned may be a cancelled group. It is the caller's
          repsonsibility to check its cancelled flag.

        ``[ HTTP: GET /api/v1/group/{groupid} ]``

        **Parameters**
          `groupid` : str
            [required] The ID or name of the group to fetch. This
            may be either the numeric ID or the short hyphenated group name (for
            example ``"100656"`` or ``"cs-editors"``).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          :any:`IbisGroup`
            The requested group or :any:`None` if it was not found.
        """
        path = "api/v1/group/%(groupid)s"
        path_params = {"groupid": groupid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.group

    def getCancelledMembers(self,
                            groupid,
                            fetch=None):
        """
        Get all the cancelled members of the specified group, including
        cancelled members of groups included by the group, and groups included
        by those groups, and so on.

        By default, only a few basic details about each member are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of each person.

        .. note::
          This method returns only cancelled people. It does not include
          people who were removed from the group. Cancelled people are no longer
          considered to be current staff, students or accredited visitors, and
          are no longer regarded as belonging to any groups or institutions. The
          list returned here reflects their group memberships just before they
          were cancelled, and so is out-of-date data that should be used with
          caution.

        ``[ HTTP: GET /api/v1/group/{groupid}/cancelled-members ]``

        **Parameters**
          `groupid` : str
            [required] The ID or name of the group.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch for each person.

        **Returns**
          list of :any:`IbisPerson`
            The group's cancelled members (in identifier order).
        """
        path = "api/v1/group/%(groupid)s/cancelled-members"
        path_params = {"groupid": groupid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

    def getDirectMembers(self,
                         groupid,
                         fetch=None):
        """
        Get the direct members of the specified group, not including members
        included via groups included by the group.

        By default, only a few basic details about each member are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of each person.

        .. note::
          This method will not include cancelled people.

        ``[ HTTP: GET /api/v1/group/{groupid}/direct-members ]``

        **Parameters**
          `groupid` : str
            [required] The ID or name of the group.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch for each person.

        **Returns**
          list of :any:`IbisPerson`
            The group's direct members (in identifier order).
        """
        path = "api/v1/group/%(groupid)s/direct-members"
        path_params = {"groupid": groupid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

    def updateDirectMembers(self,
                            groupid,
                            addIds=None,
                            removeIds=None,
                            commitComment=None):
        """
        Update the list of people who are direct members of the group. This
        will not affect people who are included in the group due to the
        inclusion of other groups.

        Any non-cancelled people in the list of identifiers specified by
        `addIds` will be added to the group. This list should be a
        comma-separated list of identifiers, each of which may be either a
        CRSid or an identifier from another identifier scheme, prefixed with
        that scheme's name and a slash. For example ``"mug99"`` or
        ``"usn/123456789"``.

        Any people in the list of identifiers specified by `removeIds`
        will be removed from the group, except if they are also in the list
        `addIds`. The special identifier ``"all-members"`` may be
        used to remove all existing group members, replacing them with the
        list specified by `newIds`.

        **Examples:**

        .. code-block:: python

          updateDirectMembers("test-group",
                              "mug99,crsid/yyy99,usn/123456789",
                              "xxx99",
                              "Remove xxx99 and add mug99, yyy99 and usn/123456789 to test-group");

        .. code-block:: python

          updateDirectMembers("test-group",
                              "xxx99,yyy99",
                              "all-members",
                              "Set the membership of test-group to include only xxx99 and yyy99");

        ``[ HTTP: PUT /api/v1/group/{groupid}/direct-members ]``

        **Parameters**
          `groupid` : str
            [required] The ID or name of the group.

          `addIds` : str
            [optional] The identifiers of people to add to the group.

          `removeIds` : str
            [optional] The identifiers of people to remove from
            the group.

          `commitComment` : str
            [recommended] A short textual description of
            the change made (will be visible on the history tab of the group and
            all the affected people in the web application).

        **Returns**
          list of :any:`IbisPerson`
            The updated list of direct members of the group (in identifier
            order).
        """
        path = "api/v1/group/%(groupid)s/direct-members"
        path_params = {"groupid": groupid}
        query_params = {}
        form_params = {"addIds": addIds,
                       "removeIds": removeIds,
                       "commitComment": commitComment}
        result = self.conn.invoke_method("PUT", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

    def getMembers(self,
                   groupid,
                   fetch=None):
        """
        Get all the members of the specified group, including members of
        groups included by the group, and groups included by those groups,
        and so on.

        By default, only a few basic details about each member are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of each person.

        .. note::
          This method will not include cancelled people.

        ``[ HTTP: GET /api/v1/group/{groupid}/members ]``

        **Parameters**
          `groupid` : str
            [required] The ID or name of the group.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch for each person.

        **Returns**
          list of :any:`IbisPerson`
            The group's members (in identifier order).
        """
        path = "api/v1/group/%(groupid)s/members"
        path_params = {"groupid": groupid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

class InstitutionMethods:
    """
    Methods for querying and manipulating institutions.

    **The fetch parameter for institutions**

    All methods that return institutions also accept an optional
    `fetch` parameter that may be used to request additional
    information about the institutions returned. For more details about
    the general rules that apply to the `fetch` parameter,
    refer to the :any:`PersonMethods` documentation.

    For institutions the `fetch` parameter may be used to fetch
    any institution attribute by specifying the `schemeid` of an
    institution attribute scheme. Examples include ``"address"``,
    ``"jpegPhoto"``, ``"universityPhone"``, ``"instPhone"``,
    ``"landlinePhone"``, ``"mobilePhone"``, ``"faxNumber"``,
    ``"email"`` and ``"labeledURI"``. The full list (which may be
    extended over time) may be obtained using :any:`InstitutionMethods.allAttributeSchemes()`.

    In addition the following pseudo-attributes are supported:

    * ``"phone_numbers"`` - fetches all phone numbers. This is
      equivalent to
      ``"universityPhone,instPhone,landlinePhone,mobilePhone"``.

    * ``"all_attrs"`` - fetches all attributes from all institution
      attribute schemes. This does not include references.

    * ``"contact_rows"`` - fetches all institution contact rows. Any
      chained fetches from contact rows are used to fetch attributes from any
      people referred to by the contact rows.

    The `fetch` parameter may also be used to fetch referenced
    people, institutions or groups. This will only include references to
    non-cancelled entities. The following references are supported:

    * ``"all_members"`` - fetches all the people who are members of the
      institution.

    * ``"parent_insts"`` - fetches all the parent institutions. Note
      that currently all institutions have only one parent, but this may change
      in the future, and client applications should be prepared to handle
      multiple parents.

    * ``"child_insts"`` - fetches all the child institutions.

    * ``"inst_groups"`` - fetches all the groups that belong to the
      institution.

    * ``"members_groups"`` - fetches all the groups that form the
      institution's membership list.

    * ``"managed_by_groups"`` - fetches all the groups that manage the
      institution's data (commonly called "Editor" groups).

    As with person `fetch` parameters, the references may be used
    in a chain by using the "dot" notation to fetch additional information
    about referenced people, institutions or groups. For example
    ``"all_members.email"`` will fetch the email addresses of all members
    of the institution. For more information about what can be fetched from
    referenced people and groups, refer to the documentation for
    :any:`PersonMethods` and :any:`GroupMethods`.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    def __init__(self, conn):
        self.conn = conn

    def allAttributeSchemes(self):
        """
        Return a list of all the institution attribute schemes available.
        The `schemeid` values of these schemes may be used in the
        `fetch` parameter of other methods that return institutions.

        ``[ HTTP: GET /api/v1/inst/all-attr-schemes ]``

        **Returns**
          list of :any:`IbisAttributeScheme`
            All the available institution attribute schemes (in precedence
            order).
        """
        path = "api/v1/inst/all-attr-schemes"
        path_params = {}
        query_params = {}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attributeSchemes

    def allInsts(self,
                 includeCancelled,
                 fetch=None):
        """
        Return a list of all institutions.

        By default, only a few basic details about each institution are
        returned, but the optional `fetch` parameter may be used
        to fetch additional attributes or references.

        ``[ HTTP: GET /api/v1/inst/all-insts ]``

        **Parameters**
          `includeCancelled` : bool
            [optional] Whether or not to include cancelled
            institutions. By default, only live institutions are returned.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisInstitution`
            The requested institutions (in instid order).
        """
        path = "api/v1/inst/all-insts"
        path_params = {}
        query_params = {"includeCancelled": includeCancelled,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.institutions

    def listInsts(self,
                  instids,
                  fetch=None):
        """
        Get the institutions with the specified IDs.

        By default, only a few basic details about each institution are
        returned, but the optional `fetch` parameter may be used
        to fetch additional attributes or references.

        The results are sorted by ID.

        .. note::
          The URL path length is limited to around 8000 characters, and
          an instid is up to 8 characters long. Allowing for comma separators
          and URL encoding, this limits the number of institutions that this
          method may fetch to around 700.

        .. note::
          The institutions returned may include cancelled institutions.
          It is the caller's repsonsibility to check their cancelled flags.

        ``[ HTTP: GET /api/v1/inst/list?instids=... ]``

        **Parameters**
          `instids` : str
            [required] A comma-separated list of instids.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisInstitution`
            The requested institutions (in instid order).
        """
        path = "api/v1/inst/list"
        path_params = {}
        query_params = {"instids": instids,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.institutions

    def search(self,
               query,
               approxMatches=None,
               includeCancelled=None,
               attributes=None,
               offset=None,
               limit=None,
               orderBy=None,
               fetch=None):
        """
        Search for institutions using a free text query string. This is the
        same search function that is used in the Lookup web application.

        By default, only a few basic details about each institution are
        returned, but the optional `fetch` parameter may be used
        to fetch additional attributes or references.

        ``[ HTTP: GET /api/v1/inst/search?query=... ]``

        **Parameters**
          `query` : str
            [required] The search string.

          `approxMatches` : bool
            [optional] Flag to enable more approximate
            matching in the search, causing more results to be returned. Defaults
            to :any:`False`.

          `includeCancelled` : bool
            [optional] Flag to allow cancelled institutions
            to be included. Defaults to :any:`False`.

          `attributes` : str
            [optional] A comma-separated list of attributes to
            consider when searching. If this is :any:`None` (the default) then
            all attribute schemes marked as searchable will be included.

          `offset` : int
            [optional] The number of results to skip at the start
            of the search. Defaults to 0.

          `limit` : int
            [optional] The maximum number of results to return.
            Defaults to 100.

          `orderBy` : str
            [optional] The order in which to list the results.
            This may be either ``"instid"`` or ``"name"`` (the default).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisInstitution`
            The matching institutions.
        """
        path = "api/v1/inst/search"
        path_params = {}
        query_params = {"query": query,
                        "approxMatches": approxMatches,
                        "includeCancelled": includeCancelled,
                        "attributes": attributes,
                        "offset": offset,
                        "limit": limit,
                        "orderBy": orderBy,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.institutions

    def searchCount(self,
                    query,
                    approxMatches=None,
                    includeCancelled=None,
                    attributes=None):
        """
        Count the number of institutions that would be returned by a search
        using a free text query string.

        ``[ HTTP: GET /api/v1/inst/search-count?query=... ]``

        **Parameters**
          `query` : str
            [required] The search string.

          `approxMatches` : bool
            [optional] Flag to enable more approximate
            matching in the search, causing more results to be returned. Defaults
            to :any:`False`.

          `includeCancelled` : bool
            [optional] Flag to allow cancelled institutions
            to be included. Defaults to :any:`False`.

          `attributes` : str
            [optional] A comma-separated list of attributes to
            consider when searching. If this is :any:`None` (the default) then
            all attribute schemes marked as searchable will be included.

        **Returns**
          int
            The number of matching institutions.
        """
        path = "api/v1/inst/search-count"
        path_params = {}
        query_params = {"query": query,
                        "approxMatches": approxMatches,
                        "includeCancelled": includeCancelled,
                        "attributes": attributes}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return int(result.value)

    def getInst(self,
                instid,
                fetch=None):
        """
        Get the institution with the specified ID.

        By default, only a few basic details about the institution are
        returned, but the optional `fetch` parameter may be used
        to fetch additional attributes or references of the institution.

        .. note::
          The institution returned may be a cancelled institution. It is
          the caller's repsonsibility to check its cancelled flag.

        ``[ HTTP: GET /api/v1/inst/{instid} ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution to fetch.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          :any:`IbisInstitution`
            The requested institution or :any:`None` if it was not found.
        """
        path = "api/v1/inst/%(instid)s"
        path_params = {"instid": instid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.institution

    def addAttribute(self,
                     instid,
                     attr,
                     position=None,
                     allowDuplicates=None,
                     commitComment=None):
        """
        Add an attribute to an institution. By default, this will not add the
        attribute again if it already exists.

        When adding an attribute, the new attribute's scheme must be set.
        In addition, either its value or its binaryData field should be set.
        All the remaining fields of the attribute are optional.

        ``[ HTTP: POST /api/v1/inst/{instid}/add-attribute ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `attr` : :any:`IbisAttribute`
            [required] The new attribute to add.

          `position` : int
            [optional] The position of the new attribute in the
            list of attributes of the same attribute scheme (1, 2, 3,...). A value
            of 0 (the default) will cause the new attribute to be added to the end
            of the list of existing attributes for the scheme.

          `allowDuplicates` : bool
            [optional] If :any:`True`, the new attribute
            will always be added, even if another identical attribute already
            exists. If :any:`False` (the default), the new attribute will only be
            added if it doesn't already exist.

          `commitComment` : str
            [recommended] A short textual description of
            the change made (will be visible on the history tab in the web
            application).

        **Returns**
          :any:`IbisAttribute`
            The newly created or existing attribute.
        """
        path = "api/v1/inst/%(instid)s/add-attribute"
        path_params = {"instid": instid}
        query_params = {}
        form_params = {"attr": attr,
                       "position": position,
                       "allowDuplicates": allowDuplicates,
                       "commitComment": commitComment}
        result = self.conn.invoke_method("POST", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attribute

    def getCancelledMembers(self,
                            instid,
                            fetch=None):
        """
        Get all the cancelled members of the specified institution.

        By default, only a few basic details about each member are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of each person.

        .. note::
          This method returns only cancelled people. It does not include
          people who were removed from the institution. Cancelled people are no
          longer considered to be current staff, students or accredited visitors,
          and are no longer regarded as belonging to any groups or institutions.
          The list returned here reflects their institutional memberships just
          before they were cancelled, and so is out-of-date data that should be
          used with caution.

        ``[ HTTP: GET /api/v1/inst/{instid}/cancelled-members ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch for each person.

        **Returns**
          list of :any:`IbisPerson`
            The institution's cancelled members (in identifier order).
        """
        path = "api/v1/inst/%(instid)s/cancelled-members"
        path_params = {"instid": instid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

    def getContactRows(self,
                       instid,
                       fetch=None):
        """
        Get all the contact rows of the specified institution.

        Any addresses, email addresses, phone numbers and web pages
        associated with the contact rows are automatically returned, as
        well as any people referred to by the contact rows.

        If any of the contact rows refer to people, then only a few basic
        details about each person are returned, but the optional
        `fetch` parameter may be used to fetch additional
        attributes or references of each person.

        .. note::
          This method will not include cancelled people.

        ``[ HTTP: GET /api/v1/inst/{instid}/contact-rows ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch for any people referred to by any
            of the contact rows.

        **Returns**
          list of :any:`IbisContactRow`
            The institution's contact rows.
        """
        path = "api/v1/inst/%(instid)s/contact-rows"
        path_params = {"instid": instid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.institution.contactRows

    def getAttributes(self,
                      instid,
                      attrs):
        """
        Get one or more (possibly multi-valued) attributes of an institution.
        The returned attributes are sorted by attribute scheme precedence and
        then attribute precedence.

        ``[ HTTP: GET /api/v1/inst/{instid}/get-attributes?attrs=... ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `attrs` : str
            [required] The attribute scheme(s) to fetch. This may
            include any number of the attributes or pseudo-attributes, but it
            may not include references or attribute chains (see the documentation
            for the `fetch` parameter in this class).

        **Returns**
          list of :any:`IbisAttribute`
            The requested attributes.
        """
        path = "api/v1/inst/%(instid)s/get-attributes"
        path_params = {"instid": instid}
        query_params = {"attrs": attrs}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attributes

    def getMembers(self,
                   instid,
                   fetch=None):
        """
        Get all the members of the specified institution.

        By default, only a few basic details about each member are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of each person.

        .. note::
          This method will not include cancelled people.

        ``[ HTTP: GET /api/v1/inst/{instid}/members ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch for each person.

        **Returns**
          list of :any:`IbisPerson`
            The institution's members (in identifier order).
        """
        path = "api/v1/inst/%(instid)s/members"
        path_params = {"instid": instid}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

    def deleteAttribute(self,
                        instid,
                        attrid,
                        commitComment=None):
        """
        Delete an attribute of an institution. It is not an error if the
        attribute does not exist.

        Note that in this method, the `commitComment` is passed
        as a query parameter, rather than as a form parameter, for greater
        client compatibility.

        ``[ HTTP: DELETE /api/v1/inst/{instid}/{attrid} ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `attrid` : long
            [required] The ID of the attribute to delete.

          `commitComment` : str
            [recommended] A short textual description of
            the change made (will be visible on the history tab in the web
            application).

        **Returns**
          bool
            :any:`True` if the attribute was deleted by this method, or
            :any:`False` if it did not exist.
        """
        path = "api/v1/inst/%(instid)s/%(attrid)s"
        path_params = {"instid": instid,
                       "attrid": attrid}
        query_params = {"commitComment": commitComment}
        form_params = {}
        result = self.conn.invoke_method("DELETE", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.value and result.value.lower() == "true"

    def getAttribute(self,
                     instid,
                     attrid):
        """
        Get a specific attribute of an institution.

        ``[ HTTP: GET /api/v1/inst/{instid}/{attrid} ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `attrid` : long
            [required] The ID of the attribute to fetch.

        **Returns**
          :any:`IbisAttribute`
            The requested attribute.
        """
        path = "api/v1/inst/%(instid)s/%(attrid)s"
        path_params = {"instid": instid,
                       "attrid": attrid}
        query_params = {}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attribute

    def updateAttribute(self,
                        instid,
                        attrid,
                        attr,
                        commitComment=None):
        """
        Update an attribute of an institution.

        The attribute's value, binaryData, comment and effective date fields
        will all be updated using the data supplied. All other fields will be
        left unchanged.

        To avoid inadvertently changing fields of the attribute, it is
        recommended that :any:`getAttribute() <InstitutionMethods.getAttribute>` be used to
        retrieve the current value of the attribute, before calling this
        method with the required changes.

        ``[ HTTP: PUT /api/v1/inst/{instid}/{attrid} ]``

        **Parameters**
          `instid` : str
            [required] The ID of the institution.

          `attrid` : long
            [required] The ID of the attribute to update.

          `attr` : :any:`IbisAttribute`
            [required] The new attribute values to apply.

          `commitComment` : str
            [recommended] A short textual description of
            the change made (will be visible on the history tab in the web
            application).

        **Returns**
          :any:`IbisAttribute`
            The updated attribute.
        """
        path = "api/v1/inst/%(instid)s/%(attrid)s"
        path_params = {"instid": instid,
                       "attrid": attrid}
        query_params = {}
        form_params = {"attr": attr,
                       "commitComment": commitComment}
        result = self.conn.invoke_method("PUT", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attribute

class PersonMethods:
    """
    Methods for querying and manipulating people.

    **Notes on the fetch parameter**

    All methods that return people, institutions or groups also accept an
    optional `fetch` parameter that may be used to request
    additional information about the entities returned. Without this
    parameter, only a few basic details about each person, institution or
    group are returned. The `fetch` parameter is quite flexible,
    and may be used in a number of different ways:

    * **Attribute fetching**. Attributes may be fetched by specifying the
      `schemeid` of an attribute scheme. For example to fetch a
      person's email addresses, use the value ``"email"``. For people common
      attribute schemes include ``"jpegPhoto"``, ``"misAffiliation"``,
      ``"title"``, ``"universityPhone"``, ``"mobexPhone"``,
      ``"landlinePhone"``, ``"mobilePhone"``, ``"pager"``,
      ``"labeledURI"`` and ``"address"``. The full list of person
      attribute schemes may be obtained using :any:`PersonMethods.allAttributeSchemes()`.

    * **Pseudo-attributes**. Certain special pseudo-attributes are defined
      for convenience. For people, the following pseudo-attributes are supported:

      * ``"phone_numbers"`` - fetches all phone numbers. This is
        equivalent to
        ``"universityPhone,instPhone,mobexPhone,landlinePhone,mobilePhone,pager"``.

      * ``"all_identifiers"`` - fetches all identifiers. Currently people
        only have CRSid identifiers, but in the future additional identifiers such
        as USN or staffNumber may be added.

      * ``"all_attrs"`` - fetches all attributes from all person attribute
        schemes. This does not include identifiers or references.

    * **Reference fetching**. For people, the following references are
      supported (and will fetch only non-cancelled institutions and groups):

      * ``"all_insts"`` - fetches all the institutions to which the person
        belongs (sorted in name order).

      * ``"all_groups"`` - fetches all the groups that the person is a
        member of, including indirect group memberships, via groups that include
        other groups.

      * ``"direct_groups"`` - fetches all the groups that the person is
        directly a member of. This does not include indirect group memberships -
        i.e., groups that include these groups.

    * **Chained reference fetching**. To fetch properties of referenced
      objects, the "dot" notation may be used. For example, to fetch the email
      addresses of all the institutions to which a person belongs, use
      ``"all_insts.email"``. Chains may include a number of reference
      following steps, for example
      ``"all_insts.managed_by_groups.all_members.email"`` will fetch all the
      institutions to which the person belongs, all the groups that manage those
      institutions, all the visible members of those groups and all the email
      addresses of those managing group members. For more information about what
      can be fetched from referenced institutions and groups, refer to the
      documentation for :any:`InstitutionMethods` and :any:`GroupMethods`.

    Multiple values of the `fetch` parameter should be separated
    by commas.

    **Fetch parameter examples**

    ``fetch = "email"``
    This fetches all the person's email addresses.

    ``fetch = "title,address"``
    This fetches all the person's titles (roles) and addresses.

    ``fetch = "all_attrs"``
    This fetches all the person's attributes.

    ``fetch = "all_groups,all_insts"``
    This fetches all the groups and institutions to which the person belongs.

    ``fetch = "all_insts.parent_insts"``
    This fetches all the person's institutions, and their parent institutions.

    ``fetch = "all_insts.email,all_insts.all_members.email"``
    This fetches all the person's institutions and their email addresses, and
    all the members of those institutions, and the email addresses of all
    those members.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    def __init__(self, conn):
        self.conn = conn

    def allAttributeSchemes(self):
        """
        Return a list of all the person attribute schemes available. The
        `schemeid` values of these schemes may be used in the
        `fetch` parameter of other methods that return people.

        .. note::
          Some of these attribute schemes are not currently used (no
          people have attribute values in the scheme). These schemes are
          reserved for possible future use.

        ``[ HTTP: GET /api/v1/person/all-attr-schemes ]``

        **Returns**
          list of :any:`IbisAttributeScheme`
            All the available person attribute schemes (in precedence
            order).
        """
        path = "api/v1/person/all-attr-schemes"
        path_params = {}
        query_params = {}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attributeSchemes

    def listPeople(self,
                   crsids,
                   fetch=None):
        """
        Get the people with the specified identifiers (typically CRSids).

        Each identifier may be either a CRSid, or an identifier from another
        identifier scheme, prefixed with that scheme's name and a slash. For
        example ``"mug99"`` or ``"usn/123456789"``.

        By default, only a few basic details about each person are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references.

        The results are sorted by identifier scheme and value.

        .. note::
          The number of people that may be fetched in a single call is
          limited by the URL path length limit (around 8000 characters). A
          CRSid is up to 7 characters long, and other identifiers are typically
          longer, since they must also include the identifier scheme. Thus the
          number of people that this method may fetch is typically limited to a
          few hundred.

        .. note::
          The people returned may include cancelled people. It is the
          caller's repsonsibility to check their cancelled flags.

        ``[ HTTP: GET /api/v1/person/list?crsids=... ]``

        **Parameters**
          `crsids` : str
            [required] A comma-separated list of identifiers.

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisPerson`
            The requested people (in identifier order).
        """
        path = "api/v1/person/list"
        path_params = {}
        query_params = {"crsids": crsids,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

    def search(self,
               query,
               approxMatches=None,
               includeCancelled=None,
               misStatus=None,
               attributes=None,
               offset=None,
               limit=None,
               orderBy=None,
               fetch=None):
        """
        Search for people using a free text query string. This is the same
        search function that is used in the Lookup web application.

        By default, only a few basic details about each person are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references.

        ``[ HTTP: GET /api/v1/person/search?query=... ]``

        **Parameters**
          `query` : str
            [required] The search string.

          `approxMatches` : bool
            [optional] Flag to enable more approximate
            matching in the search, causing more results to be returned. Defaults
            to :any:`False`.

          `includeCancelled` : bool
            [optional] Flag to allow cancelled people to
            be included (people who are no longer members of the University).
            Defaults to :any:`False`.

          `misStatus` : str
            [optional] The type of people to search for. This may
            be

            * ``"staff"`` - only include people whose MIS status is
              ``""`` (empty string), ``"staff"``, or
              ``"staff,student"``.

            * ``"student"`` - only include people whose MIS status is set to
              ``"student"`` or ``"staff,student"``.

            Otherwise all matching people will be included (the default). Note
            that the ``"staff"`` and ``"student"`` options are not
            mutually exclusive.

          `attributes` : str
            [optional] A comma-separated list of attributes to
            consider when searching. If this is :any:`None` (the default) then
            all attribute schemes marked as searchable will be included.

          `offset` : int
            [optional] The number of results to skip at the start
            of the search. Defaults to 0.

          `limit` : int
            [optional] The maximum number of results to return.
            Defaults to 100.

          `orderBy` : str
            [optional] The order in which to list the results.
            This may be either ``"identifier"`` or ``"surname"`` (the
            default).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisPerson`
            The matching people.
        """
        path = "api/v1/person/search"
        path_params = {}
        query_params = {"query": query,
                        "approxMatches": approxMatches,
                        "includeCancelled": includeCancelled,
                        "misStatus": misStatus,
                        "attributes": attributes,
                        "offset": offset,
                        "limit": limit,
                        "orderBy": orderBy,
                        "fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.people

    def searchCount(self,
                    query,
                    approxMatches=None,
                    includeCancelled=None,
                    misStatus=None,
                    attributes=None):
        """
        Count the number of people that would be returned by a search using
        a free text query string.

        ``[ HTTP: GET /api/v1/person/search-count?query=... ]``

        **Parameters**
          `query` : str
            [required] The search string.

          `approxMatches` : bool
            [optional] Flag to enable more approximate
            matching in the search, causing more results to be returned. Defaults
            to :any:`False`.

          `includeCancelled` : bool
            [optional] Flag to allow cancelled people to
            be included (people who are no longer members of the University).
            Defaults to :any:`False`.

          `misStatus` : str
            [optional] The type of people to search for. This may
            be

            * ``"staff"`` - only include people whose MIS status is
              ``""`` (empty string), ``"staff"``, or
              ``"staff,student"``.

            * ``"student"`` - only include people whose MIS status is set to
              ``"student"`` or ``"staff,student"``.

            Otherwise all matching people will be included (the default). Note
            that the ``"staff"`` and ``"student"`` options are not
            mutually exclusive.

          `attributes` : str
            [optional] A comma-separated list of attributes to
            consider when searching. If this is :any:`None` (the default) then
            all attribute schemes marked as searchable will be included.

        **Returns**
          int
            The number of matching people.
        """
        path = "api/v1/person/search-count"
        path_params = {}
        query_params = {"query": query,
                        "approxMatches": approxMatches,
                        "includeCancelled": includeCancelled,
                        "misStatus": misStatus,
                        "attributes": attributes}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return int(result.value)

    def getPerson(self,
                  scheme,
                  identifier,
                  fetch=None):
        """
        Get the person with the specified identifier.

        By default, only a few basic details about the person are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of the person.

        .. note::
          The person returned may be a cancelled person. It is the
          caller's repsonsibility to check its cancelled flag.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier} ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person to fetch
            (typically their CRSid).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          :any:`IbisPerson`
            The requested person or :any:`None` if they were not found.
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s"
        path_params = {"scheme": scheme,
                       "identifier": identifier}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.person

    def addAttribute(self,
                     scheme,
                     identifier,
                     attr,
                     position=None,
                     allowDuplicates=None,
                     commitComment=None):
        """
        Add an attribute to a person. By default, this will not add the
        attribute again if it already exists.

        When adding an attribute, the new attribute's scheme must be set.
        In addition, either its value or its binaryData field should be set.
        All the remaining fields of the attribute are optional.

        ``[ HTTP: POST /api/v1/person/{scheme}/{identifier}/add-attribute ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person to udpate
            (typically their CRSid).

          `attr` : :any:`IbisAttribute`
            [required] The new attribute to add.

          `position` : int
            [optional] The position of the new attribute in the
            list of attributes of the same attribute scheme (1, 2, 3,...). A value
            of 0 (the default) will cause the new attribute to be added to the end
            of the list of existing attributes for the scheme.

          `allowDuplicates` : bool
            [optional] If :any:`True`, the new attribute
            will always be added, even if another identical attribute already
            exists. If :any:`False` (the default), the new attribute will only be
            added if it doesn't already exist.

          `commitComment` : str
            [recommended] A short textual description of
            the change made (will be visible on the history tab in the web
            application).

        **Returns**
          :any:`IbisAttribute`
            The newly created or existing attribute.
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/add-attribute"
        path_params = {"scheme": scheme,
                       "identifier": identifier}
        query_params = {}
        form_params = {"attr": attr,
                       "position": position,
                       "allowDuplicates": allowDuplicates,
                       "commitComment": commitComment}
        result = self.conn.invoke_method("POST", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attribute

    def getAttributes(self,
                      scheme,
                      identifier,
                      attrs):
        """
        Get one or more (possibly multi-valued) attributes of a person. The
        returned attributes are sorted by attribute scheme precedence and
        then attribute precedence.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/get-attributes?attrs=... ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `attrs` : str
            [required] The attribute scheme(s) to fetch. This may
            include any number of the attributes or pseudo-attributes, but it
            may not include references or attribute chains (see the documentation
            for the `fetch` parameter in this class).

        **Returns**
          list of :any:`IbisAttribute`
            The requested attributes.
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/get-attributes"
        path_params = {"scheme": scheme,
                       "identifier": identifier}
        query_params = {"attrs": attrs}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attributes

    def getGroups(self,
                  scheme,
                  identifier,
                  fetch=None):
        """
        Get all the groups to which the specified person belongs, including
        indirect group memberships, via groups that include other groups.
        The returned list of groups is sorted by groupid.

        Note that some group memberships may not be visible to you. This
        method will only return those group memberships that you have
        permission to see.

        By default, only a few basic details about each group are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of each group.

        .. note::
          This method will not include cancelled groups.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/groups ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisGroup`
            The person's groups (in groupid order).
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/groups"
        path_params = {"scheme": scheme,
                       "identifier": identifier}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.groups

    def getInsts(self,
                 scheme,
                 identifier,
                 fetch=None):
        """
        Get all the institutions to which the specified person belongs. The
        returned list of institutions is sorted by name.

        By default, only a few basic details about each institution are
        returned, but the optional `fetch` parameter may be used
        to fetch additional attributes or references of each institution.

        .. note::
          This method will not include cancelled institutions.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/insts ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisInstitution`
            The person's institutions (in name order).
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/insts"
        path_params = {"scheme": scheme,
                       "identifier": identifier}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.institutions

    def isMemberOfGroup(self,
                        scheme,
                        identifier,
                        groupid):
        """
        Test if the specified person is a member of the specified group.

        .. note::
          This may be used with cancelled people and groups.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/is-member-of-group/{groupid} ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `groupid` : str
            [required] The ID or name of the group.

        **Returns**
          bool
            :any:`True` if the specified person is in the specified
            group, :any:`False` otherwise (or if the person or group does not
            exist).
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/is-member-of-group/%(groupid)s"
        path_params = {"scheme": scheme,
                       "identifier": identifier,
                       "groupid": groupid}
        query_params = {}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.value and result.value.lower() == "true"

    def isMemberOfInst(self,
                       scheme,
                       identifier,
                       instid):
        """
        Test if the specified person is a member of the specified institution.

        .. note::
          This may be used with cancelled people and institutions, but
          it will not include cancelled membership groups.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/is-member-of-inst/{instid} ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `instid` : str
            [required] The ID of the institution.

        **Returns**
          bool
            :any:`True` if the specified person is in the specified
            institution, :any:`False` otherwise (or if the person or institution
            does not exist).
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/is-member-of-inst/%(instid)s"
        path_params = {"scheme": scheme,
                       "identifier": identifier,
                       "instid": instid}
        query_params = {}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.value and result.value.lower() == "true"

    def getManagedGroups(self,
                         scheme,
                         identifier,
                         fetch=None):
        """
        Get all the groups that the specified person has persmission to edit.
        The returned list of groups is sorted by groupid.

        Note that some group memberships may not be visible to you. This
        method will only include groups for which you have persmission to
        see the applicable manager group memberships.

        By default, only a few basic details about each group are returned,
        but the optional `fetch` parameter may be used to fetch
        additional attributes or references of each group.

        .. note::
          This method will not include cancelled groups.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/manages-groups ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisGroup`
            The groups that the person manages (in groupid order).
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/manages-groups"
        path_params = {"scheme": scheme,
                       "identifier": identifier}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.groups

    def getManagedInsts(self,
                        scheme,
                        identifier,
                        fetch=None):
        """
        Get all the institutions that the specified person has permission to
        edit. The returned list of institutions is sorted by name.

        Note that some group memberships may not be visible to you. This
        method will only include institutions for which you have permission
        to see the applicable editor group memberships.

        By default, only a few basic details about each institution are
        returned, but the optional `fetch` parameter may be used
        to fetch additional attributes or references of each institution.

        .. note::
          This method will not include cancelled institutions.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/manages-insts ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `fetch` : str
            [optional] A comma-separated list of any additional
            attributes or references to fetch.

        **Returns**
          list of :any:`IbisInstitution`
            The institutions that the person manages (in name order).
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/manages-insts"
        path_params = {"scheme": scheme,
                       "identifier": identifier}
        query_params = {"fetch": fetch}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.institutions

    def deleteAttribute(self,
                        scheme,
                        identifier,
                        attrid,
                        commitComment=None):
        """
        Delete an attribute of a person. It is not an error if the attribute
        does not exist.

        Note that in this method, the `commitComment` is passed
        as a query parameter, rather than as a form parameter, for greater
        client compatibility.

        ``[ HTTP: DELETE /api/v1/person/{scheme}/{identifier}/{attrid} ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person to udpate
            (typically their CRSid).

          `attrid` : long
            [required] The ID of the attribute to delete.

          `commitComment` : str
            [recommended] A short textual description of
            the change made (will be visible on the history tab in the web
            application).

        **Returns**
          bool
            :any:`True` if the attribute was deleted by this method, or
            :any:`False` if it did not exist.
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/%(attrid)s"
        path_params = {"scheme": scheme,
                       "identifier": identifier,
                       "attrid": attrid}
        query_params = {"commitComment": commitComment}
        form_params = {}
        result = self.conn.invoke_method("DELETE", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.value and result.value.lower() == "true"

    def getAttribute(self,
                     scheme,
                     identifier,
                     attrid):
        """
        Get a specific attribute of a person.

        ``[ HTTP: GET /api/v1/person/{scheme}/{identifier}/{attrid} ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person (typically
            their CRSid).

          `attrid` : long
            [required] The ID of the attribute to fetch.

        **Returns**
          :any:`IbisAttribute`
            The requested attribute.
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/%(attrid)s"
        path_params = {"scheme": scheme,
                       "identifier": identifier,
                       "attrid": attrid}
        query_params = {}
        form_params = {}
        result = self.conn.invoke_method("GET", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attribute

    def updateAttribute(self,
                        scheme,
                        identifier,
                        attrid,
                        attr,
                        commitComment=None):
        """
        Update an attribute of a person.

        The attribute's value, binaryData, comment, instid and effective date
        fields will all be updated using the data supplied. All other fields
        will be left unchanged.

        To avoid inadvertently changing fields of the attribute, it is
        recommended that :any:`getAttribute() <PersonMethods.getAttribute>` be used to
        retrieve the current value of the attribute, before calling this
        method with the required changes.

        ``[ HTTP: PUT /api/v1/person/{scheme}/{identifier}/{attrid} ]``

        **Parameters**
          `scheme` : str
            [required] The person identifier scheme. Typically this
            should be ``"crsid"``, but other identifier schemes may be
            available in the future, such as ``"usn"`` or
            ``"staffNumber"``.

          `identifier` : str
            [required] The identifier of the person to udpate
            (typically their CRSid).

          `attrid` : long
            [required] The ID of the attribute to update.

          `attr` : :any:`IbisAttribute`
            [required] The new attribute values to apply.

          `commitComment` : str
            [recommended] A short textual description of
            the change made (will be visible on the history tab in the web
            application).

        **Returns**
          :any:`IbisAttribute`
            The updated attribute.
        """
        path = "api/v1/person/%(scheme)s/%(identifier)s/%(attrid)s"
        path_params = {"scheme": scheme,
                       "identifier": identifier,
                       "attrid": attrid}
        query_params = {}
        form_params = {"attr": attr,
                       "commitComment": commitComment}
        result = self.conn.invoke_method("PUT", path, path_params,
                                         query_params, form_params)
        if result.error:
            raise IbisException(result.error)
        return result.attribute
