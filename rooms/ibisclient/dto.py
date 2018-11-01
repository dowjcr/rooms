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
#
# Author: Dean Rasheed (dev-group@ucs.cam.ac.uk)
# --------------------------------------------------------------------------

"""
DTO classes for transferring data from the server to client in the web
service API.

All web service API methods return an instance or a list of one of these DTO
classes, or a primitive type such as a bool, int or string.

In the case of an error, an :any:`IbisException` will be raised which will
contain an instance of an :any:`IbisError` DTO.
"""

import base64
from datetime import date
from xml.parsers import expat

import sys
if sys.hexversion < 0x02040000:
    from sets import Set as set

_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class IbisDto(object):
    """
    Base class for all DTO classes.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    # All properties
    __slots__ = []

    # Properties marked as @XmlAttribte in the JAXB class
    xml_attrs = set()

    # Properties marked as @XmlElement in the JAXB class
    xml_elems = set()

    # Properties marked as @XmlElementWrapper in the JAXB class
    xml_arrays = set()

    def __init__(self, attrs={}):
        """
        Create an IbisDto from the attributes of an XML node. This just
        sets the properties marked as @XmlAttribute in the JAXB class.
        """
        for attr in self.__class__.__slots__:
            setattr(self, attr, None)
        for attr in self.__class__.xml_attrs:
            setattr(self, attr, attrs.get(attr))

    def start_child_element(self, tagname):
        """
        Start element callback invoked during XML parsing when the opening
        tag of a child element is encountered. This creates and returns any
        properties marked as @XmlElementWrapper in the JAXB class, so that
        child collections can be populated.
        """
        if tagname in self.__class__.xml_arrays:
            if getattr(self, tagname) == None: setattr(self, tagname, [])
            return getattr(self, tagname)
        return None

    def end_child_element(self, tagname, data):
        """
        End element callback invoked during XML parsing when the end tag of
        a child element is encountered, and the tag's data is available. This
        sets the value of any properties marked as @XmlElement in the JAXB
        class.
        """
        if tagname in self.__class__.xml_elems:
            setattr(self, tagname, data)

# --------------------------------------------------------------------------
# IbisPerson: see uk.ac.cam.ucs.ibis.dto.IbisPerson.java
# --------------------------------------------------------------------------
class IbisPerson(IbisDto):
    """
    Class representing a person returned by the web service API. Note that
    the identifier is the person's primary identifier (typically their CRSid),
    regardless of which identifier was used to query for the person.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "cancelled":
            """
            bool
              Flag indicating if the person is cancelled.
            """,
        "identifier":
            """
            :any:`IbisIdentifier`
              The person's primary identifier (typically their CRSid).
            """,
        "displayName":
            """
            str
              The person's display name (if visible).
            """,
        "registeredName":
            """
            str
              The person's registered name (if visible).
            """,
        "surname":
            """
            str
              The person's surname (if visible).
            """,
        "visibleName":
            """
            str
              The person's display name if that is visible, otherwise their
              registered name if that is visible, otherwise their surname if
              that is visible, otherwise the value of their primary identifier
              (typically their CRSid) which is always visible.
            """,
        "misAffiliation":
            """
            str
              The person's MIS status (``"staff"``, ``"student"``,
              ``"staff,student"`` or ``""``).
            """,
        "identifiers":
            """
            list of :any:`IbisIdentifier`
              A list of the person's identifiers. This will only be populated
              if the `fetch` parameter included the ``"all_identifiers"``
              option.
            """,
        "attributes":
            """
            list of :any:`IbisAttribute`
              A list of the person's attributes. This will only be populated
              if the `fetch` parameter includes the ``"all_attrs"`` option, or
              any specific attribute schemes such as ``"email"`` or
              ``"title"``, or the special pseudo-attribute scheme
              ``"phone_numbers"``.
            """,
        "institutions":
            """
            list of :any:`IbisInstitution`
              A list of all the institution's to which the person belongs.
              This will only be populated if the `fetch` parameter includes
              the ``"all_insts"`` option.
            """,
        "groups":
            """
            list of :any:`IbisGroup`
              A list of all the groups to which the person belongs, including
              indirect group memberships, via groups that include other
              groups. This will only be populated if the `fetch` parameter
              includes the ``"all_groups"`` option.
            """,
        "directGroups":
            """
            list of :any:`IbisGroup`
              A list of all the groups that the person directly belongs to.
              This does not include indirect group memberships - i.e., groups
              that include these groups. This will only be populated if the
              `fetch` parameter includes the ``"direct_groups"`` option.
            """,
        "id":
            """
            str
              An ID that can uniquely identify this person within the returned
              XML/JSON document. This is only used in the flattened XML/JSON
              representation (if the "flatten" parameter is specified).
            """,
        "ref":
            """
            str
              A reference (by id) to a person element in the XML/JSON
              document. This is only used in the flattened XML/JSON
              representation (if the "flatten" parameter is specified).
            """,
        "unflattened":
            """
            bool
              Flag to prevent infinite recursion due to circular references.
            """
    }

    xml_attrs = set(["cancelled", "id", "ref"])

    xml_elems = set(["identifier", "displayName", "registeredName",
                     "surname", "visibleName", "misAffiliation"])

    xml_arrays = set(["identifiers", "attributes", "institutions",
                      "groups", "directGroups"])

    def __init__(self, attrs={}):
        """ Create an IbisPerson from the attributes of an XML node. """
        IbisDto.__init__(self, attrs)
        if self.cancelled != None:
            self.cancelled = self.cancelled.lower() == "true"
        self.unflattened = False

    def is_staff(self):
        """
        Returns :any:`True` if the person is a member of staff.

        Note that this tests for an misAffiliation of ``""``, ``"staff"`` or
        ``"staff,student"`` since some members of staff will have a blank
        misAffiliation.
        """
        return self.misAffiliation == None or\
               self.misAffiliation != "student";

    def is_student(self):
        """
        Returns :any:`True` if the person is a student.

        This tests for an misAffiliation of ``"student"`` or
        ``"staff,student"``.
        """
        return self.misAffiliation != None and\
               self.misAffiliation.find("student") != -1;

    def unflatten(self, em):
        """ Unflatten a single IbisPerson. """
        if self.ref:
            person = em.get_person(self.ref)
            if not person.unflattened:
                person.unflattened = True
                unflatten_insts(em, person.institutions)
                unflatten_groups(em, person.groups)
                unflatten_groups(em, person.directGroups)
            return person
        return self

def unflatten_people(em, people):
    """ Unflatten a list of IbisPerson objects (done in place). """
    if people:
        for idx, person in enumerate(people):
            people[idx] = person.unflatten(em)

# --------------------------------------------------------------------------
# IbisInstitution: see uk.ac.cam.ucs.ibis.dto.IbisInstitution.java
# --------------------------------------------------------------------------
class IbisInstitution(IbisDto):
    """
    Class representing an institution returned by the web service API.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "cancelled":
            """
            bool
              Flag indicating if the institution is cancelled.
            """,
        "instid":
            """
            str
              The institution's unique ID (e.g., ``"CS"``).
            """,
        "name":
            """
            str
              The institution's name.
            """,
        "acronym":
            """
            str
              The institution's acronym, if set (e.g., ``"UCS"``).
            """,
        "attributes":
            """
            list of :any:`IbisAttribute`
              A list of the institution's attributes. This will only be
              populated if the `fetch` parameter includes the ``"all_attrs"``
              option, or any specific attribute schemes such as ``"email"`` or
              ``"address"``, or the special pseudo-attribute scheme
              ``"phone_numbers"``.
            """,
        "contactRows":
            """
            list of :any:`IbisContactRow`
              A list of the institution's contact rows. This will only be
              populated if the `fetch` parameter includes the
              ``"contact_rows"`` option.
            """,
        "members":
            """
            list of :any:`IbisPerson`
              A list of the institution's members. This will only be populated
              if the `fetch` parameter includes the ``"all_members"`` option.
            """,
        "parentInsts":
            """
            list of :any:`IbisInstitution`
              A list of the institution's parent institutions. This will only
              be populated if the `fetch` parameter includes the
              ``"parent_insts"`` option.

              .. note::
                Currently all institutions have one parent, but in the future
                institutions may have multiple parents.
            """,
        "childInsts":
            """
            list of :any:`IbisInstitution`
              A list of the institution's child institutions. This will only
              be populated if the `fetch` parameter includes the
              ``"child_insts"`` option.
            """,
        "groups":
            """
            list of :any:`IbisGroup`
              A list of all the groups that belong to the institution. This
              will only be populated if the `fetch` parameter includes the
              ``"inst_groups"`` option.
            """,
        "membersGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups that form the institution's membership.
              This will only be populated if the `fetch` parameter includes
              the ``"members_groups"`` option.
            """,
        "managedByGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups that manage this institution. This will
              only be populated if the `fetch` parameter includes the
              ``"managed_by_groups"`` option.
            """,
        "id":
            """
            str
              An ID that can uniquely identify this institution within the
              returned XML/JSON document. This is only used in the flattened
              XML/JSON representation (if the "flatten" parameter is
              specified).
            """,
        "ref":
            """
            str
              A reference (by id) to an institution element in the XML/JSON
              document. This is only used in the flattened XML/JSON
              representation (if the "flatten" parameter is specified).
            """,
        "unflattened":
            """
            bool
              Flag to prevent infinite recursion due to circular references.
            """
    }

    xml_attrs = set(["cancelled", "instid", "id", "ref"])

    xml_elems = set(["name", "acronym"])

    xml_arrays = set(["attributes", "contactRows", "members",
                      "parentInsts", "childInsts", "groups",
                      "membersGroups", "managedByGroups"])

    def __init__(self, attrs={}):
        """ Create an IbisInstitution from the attributes of an XML node. """
        IbisDto.__init__(self, attrs)
        if self.cancelled != None:
            self.cancelled = self.cancelled.lower() == "true"
        self.unflattened = False

    def unflatten(self, em):
        """ Unflatten a single IbisInstitution. """
        if self.ref:
            inst = em.get_institution(self.ref)
            if not inst.unflattened:
                inst.unflattened = True
                unflatten_contact_rows(em, inst.contactRows)
                unflatten_people(em, inst.members)
                unflatten_insts(em, inst.parentInsts)
                unflatten_insts(em, inst.childInsts)
                unflatten_groups(em, inst.groups)
                unflatten_groups(em, inst.membersGroups)
                unflatten_groups(em, inst.managedByGroups)
            return inst
        return self

def unflatten_insts(em, insts):
    """ Unflatten a list of IbisInstitution objects (done in place). """
    if insts:
        for idx, inst in enumerate(insts):
            insts[idx] = inst.unflatten(em)

# --------------------------------------------------------------------------
# IbisGroup: see uk.ac.cam.ucs.ibis.dto.IbisGroup.java
# --------------------------------------------------------------------------
class IbisGroup(IbisDto):
    """
    Class representing a group returned by the web service API.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "cancelled":
            """
            bool
              Flag indicating if the group is cancelled.
            """,
        "groupid":
            """
            str
              The group's numeric ID (actually a string e.g., ``"100656"``).
            """,
        "name":
            """
            str
              The group's unique name (e.g., ``"cs-editors"``).
            """,
        "title":
            """
            str
              The group's title.
            """,
        "description":
            """
            str
              The more detailed description of the group.
            """,
        "email":
            """
            str
              The group's email address.
            """,
        "membersOfInst":
            """
            :any:`IbisInstitution`
              The details of the institution for which this group forms all
              or part of the membership. This will only be set for groups that
              are membership groups of institutions if the `fetch` parameter
              includes the ``"members_of_inst"`` option.
            """,
        "members":
            """
            list of :any:`IbisPerson`
              A list of the group's members, including (recursively) any
              members of any included groups. This will only be populated if
              the `fetch` parameter includes the ``"all_members"`` option.
            """,
        "directMembers":
            """
            list of :any:`IbisPerson`
              A list of the group's direct members, not including any members
              included via groups included by this group. This will only be
              populated if the `fetch` parameter includes the
              ``"direct_members"`` option.
            """,
        "owningInsts":
            """
            list of :any:`IbisInstitution`
              A list of the institutions to which this group belongs. This
              will only be populated if the `fetch` parameter includes the
              ``"owning_insts"`` option.
            """,
        "managesInsts":
            """
            list of :any:`IbisInstitution`
              A list of the institutions managed by this group. This will only
              be populated if the `fetch` parameter includes the
              ``"manages_insts"`` option.
            """,
        "managesGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups managed by this group. This will only be
              populated if the `fetch` parameter includes the
              ``"manages_groups"`` option.
            """,
        "managedByGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups that manage this group. This will only be
              populated if the `fetch` parameter includes the
              ``"managed_by_groups"`` option.
            """,
        "readsGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups that this group has privileged access to.
              Members of this group will be able to read the members of any of
              those groups, regardless of the membership visibilities. This
              will only be populated if the `fetch` parameter includes the
              ``"reads_groups"`` option.
            """,
        "readByGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups that have privileged access to this group.
              Members of those groups will be able to read the members of this
              group, regardless of the membership visibilities. This will only
              be populated if the `fetch` parameter includes the
              ``"read_by_groups"`` option.
            """,
        "includesGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups directly included in this group. Any
              members of the included groups (and recursively any groups that
              they include) will automatically be included in this group. This
              will only be populated if the `fetch` parameter includes the
              ``"includes_groups"`` option.
            """,
        "includedByGroups":
            """
            list of :any:`IbisGroup`
              A list of the groups that directly include this group. Any
              members of this group will automatically be included in those
              groups (and recursively in any groups that include those
              groups). This will only be populated if the `fetch` parameter
              includes the ``"included_by_groups"`` option.
            """,
        "id":
            """
            str
              An ID that can uniquely identify this group within the returned
              XML/JSON document. This is only used in the flattened XML/JSON
              representation (if the "flatten" parameter is specified).
            """,
        "ref":
            """
            str
              A reference (by id) to a group element in the XML/JSON document.
              This is only used in the flattened XML/JSON representation (if
              the "flatten" parameter is specified).
            """,
        "unflattened":
            """
            bool
              Flag to prevent infinite recursion due to circular references.
            """
    }

    xml_attrs = set(["cancelled", "groupid", "id", "ref"])

    xml_elems = set(["name", "title", "description", "emails",
                     "membersOfInst"])

    xml_arrays = set(["members", "directMembers",
                      "owningInsts", "managesInsts",
                      "managesGroups", "managedByGroups",
                      "readsGroups", "readByGroups",
                      "includesGroups", "includedByGroups"])

    def __init__(self, attrs={}):
        """ Create an IbisGroup from the attributes of an XML node. """
        IbisDto.__init__(self, attrs)
        if self.cancelled != None:
            self.cancelled = self.cancelled.lower() == "true"
        self.unflattened = False

    def unflatten(self, em):
        """ Unflatten a single IbisGroup. """
        if self.ref:
            group = em.get_group(self.ref)
            if not group.unflattened:
                group.unflattened = True
                if group.membersOfInst:
                    group.membersOfInst = group.membersOfInst.unflatten(em)
                unflatten_people(em, group.members)
                unflatten_people(em, group.directMembers)
                unflatten_insts(em, group.owningInsts)
                unflatten_insts(em, group.managesInsts)
                unflatten_groups(em, group.managesGroups)
                unflatten_groups(em, group.managedByGroups)
                unflatten_groups(em, group.readsGroups)
                unflatten_groups(em, group.readByGroups)
                unflatten_groups(em, group.includesGroups)
                unflatten_groups(em, group.includedByGroups)
            return group
        return self

def unflatten_groups(em, groups):
    """ Unflatten a list of IbisGroup objects (done in place). """
    if groups:
        for idx, group in enumerate(groups):
            groups[idx] = group.unflatten(em)

# --------------------------------------------------------------------------
# IbisIdentifier: see uk.ac.cam.ucs.ibis.dto.IbisIdentifier.java
# --------------------------------------------------------------------------
class IbisIdentifier(IbisDto):
    """
    Class representing a person's identifier, for use by the web service
    API.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "scheme":
            """
            str
              The identifier's scheme (e.g., ``"crsid"``).
            """,
        "value":
            """
            str
              The identifier's value in that scheme (e.g., a specific CRSid
              value).
            """
    }

    xml_attrs = set(["scheme"])

# --------------------------------------------------------------------------
# IbisAttribute: see uk.ac.cam.ucs.ibis.dto.IbisAttribute.java
# --------------------------------------------------------------------------
class IbisAttribute(IbisDto):
    """
    Class representing an attribute of a person or institution returned by
    the web service API. Note that for institution attributes, the
    :any:`instid <IbisAttribute.instid>`,
    :any:`visibility <IbisAttribute.visibility>` and
    :any:`owningGroupid <IbisAttribute.owningGroupid>` fields will be
    :any:`None`.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "attrid":
            """
            int
              The unique internal identifier of the attribute.
            """,
        "scheme":
            """
            str
              The attribute's scheme.
            """,
        "value":
            """
            str
              The attribute's value (except for binary attributes).
            """,
        "binaryData":
            """
            bytes
              The binary data held in the attribute (e.g., a JPEG photo).
            """,
        "comment":
            """
            str
              Any comment associated with the attribute.
            """,
        "instid":
            """
            str
              For a person attribute, the optional institution that the
              attribute is associated with. This will not be set for
              institution attributes.
            """,
        "visibility":
            """
            str
              For a person attribute, it's visibility (``"private"``,
              ``"institution"``, ``"university"`` or ``"world"``). This will
              not be set for institution attributes.
            """,
        "effectiveFrom":
            """
            date
              For time-limited attributes, the date from which it takes
              effect.
            """,
        "effectiveTo":
            """
            date
              For time-limited attributes, the date after which it is no
              longer effective.
            """,
        "owningGroupid":
            """
            str
              For a person attribute, the ID of the group that owns it
              (typically the user agent group that created it).
            """
    }

    xml_attrs = set(["attrid", "scheme", "instid", "visibility",
                     "effectiveFrom", "effectiveTo", "owningGroupid"])

    xml_elems = set(["value", "binaryData", "comment"])

    def __init__(self, attrs={}):
        """ Create an IbisAttribute from the attributes of an XML node. """
        IbisDto.__init__(self, attrs)
        if self.attrid != None:
            self.attrid = int(self.attrid)
        if self.effectiveFrom != None:
            self.effectiveFrom = parse_date(self.effectiveFrom)
        if self.effectiveTo != None:
            self.effectiveTo = parse_date(self.effectiveTo)

    def end_child_element(self, tagname, data):
        """
        Overridden end element callback to decode binary data.
        """
        IbisDto.end_child_element(self, tagname, data)
        if tagname == "binaryData" and self.binaryData != None:
            self.binaryData = base64.b64decode(self.binaryData)

    def encoded_string(self):
        """
        Encode this attribute as an ASCII string suitable for passing as a
        parameter to a web service API method. This string is compatible with
        `valueOf(java.lang.String)` on the corresponding Java class,
        used on the server to decode the attribute parameter.

        .. note::
          This requires that the attribute's
          :any:`scheme <IbisAttribute.scheme>` field be set, and typically the
          :any:`value <IbisAttribute.value>` or
          :any:`binaryData <IbisAttribute.binaryData>` should also be set.

        **Returns**
          str
            The string encoding of this attribute.
        """
        if not self.scheme:
            raise ValueError("Attribute scheme must be set")

        result = "scheme:%s" % base64.b64encode(self.scheme)
        if self.attrid != None:
            result = "%s,attrid:%d" % (result, self.attrid)
        if self.value != None:
            result = "%s,value:%s" % (result, base64.b64encode(self.value))
        if self.binaryData != None:
            result = "%s,binaryData:%s" %\
                     (result, base64.b64encode(self.binaryData))
        if self.comment != None:
            result = "%s,comment:%s" %\
                     (result, base64.b64encode(self.comment))
        if self.instid != None:
            result = "%s,instid:%s" %\
                     (result, base64.b64encode(self.instid))
        if self.visibility != None:
            result = "%s,visibility:%s" %\
                     (result, base64.b64encode(self.visibility))
        if self.effectiveFrom != None:
            result = "%s,effectiveFrom:%02d %s %d" %\
                     (result,
                      self.effectiveFrom.day,
                      _MONTHS[self.effectiveFrom.month-1],
                      self.effectiveFrom.year)
        if self.effectiveTo != None:
            result = "%s,effectiveTo:%02d %s %d" %\
                     (result,
                      self.effectiveTo.day,
                      _MONTHS[self.effectiveTo.month-1],
                      self.effectiveTo.year)
        if self.owningGroupid != None:
            result = "%s,owningGroupid:%s" %\
                     (result, base64.b64encode(self.owningGroupid))
        return result

def parse_date(s):
    """ Parse a date string from XML. """
    s = s.strip()
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))

# --------------------------------------------------------------------------
# IbisError: see uk.ac.cam.ucs.ibis.dto.IbisError.java
# --------------------------------------------------------------------------
class IbisError(IbisDto):
    """
    Class representing an error returned by the web service API.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "status":
            """
            int
              The HTTP error status code.
            """,
        "code":
            """
            str
              A short textual description of the error status code.
            """,
        "message":
            """
            str
              A short textual description of the error message (typically one
              line).
            """,
        "details":
            """
            str
              The full details of the error (e.g., a Java stack trace).
            """
    }

    xml_attrs = set(["status"])

    xml_elems = set(["code", "message", "details"])

    def __init__(self, attrs={}):
        """ Create an IbisError from the attributes of an XML node. """
        IbisDto.__init__(self, attrs)
        if self.status != None:
            self.status = int(self.status)

# --------------------------------------------------------------------------
# IbisAttributeScheme: see uk.ac.cam.ucs.ibis.dto.IbisAttributeScheme.java
# --------------------------------------------------------------------------
class IbisAttributeScheme(IbisDto):
    """
    Class representing an attribute scheme. This may apply to attributes of
    people or institutions.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "schemeid":
            """
            str
              The unique identifier of the attribute scheme.
            """,
        "precedence":
            """
            int
              The attribute scheme's precedence. Methods that return or
              display attributes sort the results primarily in order of
              increasing values of attribute scheme precedence.
            """,
        "ldapName":
            """
            str
              The name of the attribute scheme in LDAP, if it is exported to
              LDAP. Note that many attributes are not exported to LDAP, in
              which case this name is typically just equal to the scheme's ID.
            """,
        "displayName":
            """
            str
              The display name for labelling attributes in this scheme.
            """,
        "dataType":
            """
            str
              The attribute scheme's datatype.
            """,
        "multiValued":
            """
            bool
              Flag indicating whether attributes in this scheme can be
              multi-valued.
            """,
        "multiLined":
            """
            bool
              Flag for textual attributes schemes indicating whether they are
              multi-lined.
            """,
        "searchable":
            """
            bool
              Flag indicating whether attributes of this scheme are searched
              by the default search functionality.
            """,
        "regexp":
            """
            str
              For textual attributes, an optional regular expression that all
              attributes in this scheme match.
            """
    }

    xml_attrs = set(["schemeid", "precedence", "multiValued", "multiLined",
                     "searchable"])

    xml_elems = set(["ldapName", "displayName", "dataType", "regexp"])

    def __init__(self, attrs={}):
        """
        Create an IbisAttributeScheme from the attributes of an XML node.
        """
        IbisDto.__init__(self, attrs)
        if self.precedence != None:
            self.precedence = int(self.precedence)
        if self.multiValued != None:
            self.multiValued = self.multiValued.lower() == "true"
        if self.multiLined != None:
            self.multiLined = self.multiLined.lower() == "true"
        if self.searchable != None:
            self.searchable = self.searchable.lower() == "true"

# --------------------------------------------------------------------------
# IbisContactRow: see uk.ac.cam.ucs.ibis.dto.IbisContactRow.java
# --------------------------------------------------------------------------
class IbisContactRow(IbisDto):
    """
    Class representing an institution contact row, for use by the web
    services API.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "description":
            """
            str
              The contact row's text.
            """,
        "bold":
            """
            bool
              Flag indicating if the contact row's text is normally displayed
              in bold.
            """,
        "italic":
            """
            bool
              Flag indicating if the contact row's text is normally displayed
              in italics.
            """,
        "addresses":
            """
            list of str
              A list of the contact row's addresses. This will never be
              :any:`None`, but it may be an empty list.
            """,
        "emails":
            """
            list of str
              A list of the contact row's email addresses. This will never be
              :any:`None`, but it may be an empty list.
            """,
        "people":
            """
            list of :any:`IbisPerson`
              A list of the people referred to by the contact row. This will
              never by :any:`None`, but it may be an empty list.
            """,
        "phoneNumbers":
            """
            list of :any:`IbisContactPhoneNumber`
              A list of the contact row's phone numbers. This will never be
              :any:`None`, but it may be an empty list.
            """,
        "webPages":
            """
            list of :any:`IbisContactWebPage`
              A list of the contact row's web pages. This will never be
              :any:`None`, but it may be an empty list.
            """,
        "unflattened":
            """
            bool
              Flag to prevent infinite recursion due to circular references.
            """
    }

    xml_attrs = set(["bold", "italic"])

    xml_elems = set(["description"])

    xml_arrays = set(["addresses", "emails", "people", "phoneNumbers",
                      "webPages"])

    def __init__(self, attrs={}):
        """ Create an IbisContactRow from the attributes of an XML node. """
        IbisDto.__init__(self, attrs)
        if self.bold != None:
            self.bold = self.bold.lower() == "true"
        if self.italic != None:
            self.italic = self.italic.lower() == "true"
        self.unflattened = False

    def unflatten(self, em):
        """ Unflatten a single IbisContactRow. """
        if not self.unflattened:
            self.unflattened = True
            unflatten_people(em, self.people)
        return self

def unflatten_contact_rows(em, contact_rows):
    """ Unflatten a list of IbisContactRow objects (done in place). """
    if contact_rows:
        for idx, contact_row in enumerate(contact_rows):
            contact_rows[idx] = contact_row.unflatten(em)

# --------------------------------------------------------------------------
# IbisContactPhoneNumber:
#     see uk.ac.cam.ucs.ibis.dto.IbisContactPhoneNumber.java
# --------------------------------------------------------------------------
class IbisContactPhoneNumber(IbisDto):
    """
    Class representing a phone number held on an institution contact row, for
    use by the web service API.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "phoneType":
            """
            str
              The phone number's type.
            """,
        "number":
            """
            str
              The phone number.
            """,
        "comment":
            """
            str
              Any comment associated with the phone number.
            """
    }

    xml_attrs = set(["phoneType"])

    xml_elems = set(["number", "comment"])

# --------------------------------------------------------------------------
# IbisContactWebPage: see uk.ac.cam.ucs.ibis.dto.IbisContactWebPage.java
# --------------------------------------------------------------------------
class IbisContactWebPage(IbisDto):
    """
    Class representing a web page referred to by an institution contact row,
    for use by the web service API.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "url":
            """
            str
              The web page's URL.
            """,
        "label":
            """
            str
              The web page's label (link text) if set.
            """
    }

    xml_elems = set(["url", "label"])

# --------------------------------------------------------------------------
# IbisResult: see uk.ac.cam.ucs.ibis.dto.IbisResult.java
# --------------------------------------------------------------------------
class IbisResult(IbisDto):
    """
    Class representing the top-level container for all results.

    This may be just a simple textual value or it may contain more complex
    entities such as people, institutions, groups, attributes, etc.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    __slots__ = {
        "version":
            """
            str
              The web service API version number.
            """,
        "value":
            """
            str
              The value returned by methods that return a simple textual
              value.
            """,
        "person":
            """
            :any:`IbisPerson`
              The person returned by methods that return a single person.

              Note that methods that may return multiple people will always
              use the :any:`people <IbisResult.people>` field, even if only
              one person was returned.
            """,
        "institution":
            """
            :any:`IbisInstitution`
              The institution returned by methods that return a single
              institution.

              Note that methods that may return multiple institutions will
              always use the :any:`institutions <IbisResult.institutions>`
              field, even if only one institution was returned.
            """,
        "group":
            """
            :any:`IbisGroup`
              The group returned by methods that return a single group.

              Note that methods that may return multiple groups will always
              use the :any:`groups <IbisResult.groups>` field, even if only
              one group was returned.
            """,
        "identifier":
            """
            :any:`IbisIdentifier`
              The identifier returned by methods that return a single
              identifier.
            """,
        "attribute":
            """
            :any:`IbisAttribute`
              The person or institution attribute returned by methods that
              return a single attribute.
            """,
        "error":
            """
            :any:`IbisError`
              If the method failed, details of the error.
            """,
        "people":
            """
            list of :any:`IbisPerson`
              The list of people returned by methods that may return multiple
              people. This may be empty, or contain one or more people.
            """,
        "institutions":
            """
            list of :any:`IbisInstitution`
              The list of institutions returned by methods that may return
              multiple institutions. This may be empty, or contain one or more
              institutions.
            """,
        "groups":
            """
            list of :any:`IbisGroup`
              The list of groups returned by methods that may return multiple
              groups. This may be empty, or contain one or more groups.
            """,
        "attributes":
            """
            list of :any:`IbisAttribute`
              The list of attributes returned by methods that return lists of
              person/institution attributes.
            """,
        "attributeSchemes":
            """
            list of :any:`IbisAttributeScheme`
              The list of attribute schemes returned by methods that return
              lists of person/institution attribute schemes.
            """,
        "entities":
            """
            :any:`IbisResult.Entities`
              In the flattened XML/JSON representation, all the unique
              entities returned by the method.

              .. note::
                This will be :any:`None` unless the "flatten" parameter is
                :any:`True`.
            """
    }

    xml_attrs = set(["version"])

    xml_elems = set(["value", "person", "institution", "group",
                     "identifier", "attribute", "error", "entities"])

    xml_arrays = set(["people", "institutions", "groups",
                      "attributes", "attributeSchemes"])

    class Entities(IbisDto):
        """
        Nested class to hold the full details of all the entities returned
        in a result. This is used only in the flattened result representation,
        where each of these entities will have a unique textual ID, and be
        referred to from the top-level objects returned (and by each other).

        In the hierarchical representation, this is not used, since all
        entities returned will be at the top-level, or directly contained in
        those top-level entities.

        .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
        """
        __slots__ = {
            "people":
                """
                list of :any:`IbisPerson`
                  A list of all the unique people returned by the method. This
                  may include additional people returned as a result of the
                  `fetch` parameter, so this list may contain more entries
                  than the corresponding field on the enclosing class.
                """,
            "institutions":
                """
                list of :any:`IbisInstitution`
                  A list of all the unique institutions returned by the
                  method. This may include additional institutions returned as
                  a result of the `fetch` parameter, so this list may contain
                  more entries than the corresponding field on the enclosing
                  class.
                """,
            "groups":
                """
                list of :any:`IbisGroup`
                  A list of all the unique groups returned by the method. This
                  may include additional groups returned as a result of the
                  `fetch` parameter, so this list may contain more entries
                  than the corresponding field on the enclosing class.
                """
        }

        xml_arrays = set(["people", "institutions", "groups"])

    class EntityMap:
        """
        Nested class to assist during the unflattening process, maintaining
        efficient maps from IDs to entities (people, institutions and groups).

        .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
        """
        def __init__(self, result):
            """
            Construct an entity map from a flattened IbisResult.
            """
            self.people_by_id = {}
            self.insts_by_id = {}
            self.groups_by_id = {}

            if result.entities.people:
                for person in result.entities.people:
                    self.people_by_id[person.id] = person
            if result.entities.institutions:
                for inst in result.entities.institutions:
                    self.insts_by_id[inst.id] = inst
            if result.entities.groups:
                for group in result.entities.groups:
                    self.groups_by_id[group.id] = group

        def get_person(self, id):
            """
            Get a person from the entity map, given their ID.
            """
            return self.people_by_id.get(id)

        def get_institution(self, id):
            """
            Get an institution from the entity map, given its ID.
            """
            return self.insts_by_id.get(id)

        def get_group(self, id):
            """
            Get a group from the entity map, given its ID.
            """
            return self.groups_by_id.get(id)

    def unflatten(self):
        """
        Unflatten this IbisResult object, resolving any internal ID refs
        to build a fully fledged object tree.

        This is necessary if the IbisResult was constructed from XML/JSON in
        its flattened representation (with the "flatten" parameter set to
        :any:`True`).

        On entry, the IbisResult object may have people, institutions or
        groups in it with "ref" fields referring to objects held in the
        "entities" lists. After unflattening, all such references will have
        been replaced by actual object references, giving an object tree that
        can be traversed normally.

        Returns this IbisResult object, with its internals unflattened.
        """
        if self.entities:
            em = IbisResult.EntityMap(self)

            if self.person:
                self.person = self.person.unflatten(em)
            if self.institution:
                self.institution = self.institution.unflatten(em)
            if self.group:
                self.group = self.group.unflatten(em)

            unflatten_people(em, self.people)
            unflatten_insts(em, self.institutions)
            unflatten_groups(em, self.groups)

        return self

# --------------------------------------------------------------------------
# IbisResultParser: unmarshaller for IbisResult objects
# --------------------------------------------------------------------------
class IbisResultParser:
    """
    Class to parse the XML from the server and produce an IbisResult.

    .. codeauthor:: Dean Rasheed (dev-group@ucs.cam.ac.uk)
    """
    def __init__(self):
        self.result = None
        self.node_stack = []
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.EndElementHandler = self.end_element
        self.parser.CharacterDataHandler = self.char_data

    def start_element(self, tagname, attrs):
        element = None
        if self.node_stack:
            if tagname == "person":
                element = IbisPerson(attrs)
            elif tagname == "institution":
                element = IbisInstitution(attrs)
            elif tagname == "membersOfInst":
                element = IbisInstitution(attrs)
            elif tagname == "group":
                element = IbisGroup(attrs)
            elif tagname == "identifier":
                element = IbisIdentifier(attrs)
            elif tagname == "attribute":
                element = IbisAttribute(attrs)
            elif tagname == "error":
                element = IbisError(attrs)
            elif tagname == "attributeScheme":
                element = IbisAttributeScheme(attrs)
            elif tagname == "contactRow":
                element = IbisContactRow(attrs)
            elif tagname == "phoneNumber":
                element = IbisContactPhoneNumber(attrs)
            elif tagname == "webPage":
                element = IbisContactWebPage(attrs)
            elif tagname == "entities":
                element = IbisResult.Entities(attrs)
            else:
                parent = self.node_stack[-1]
                if (not isinstance(parent, list)) and\
                   (not isinstance(parent, dict)):
                    element = parent.start_child_element(tagname)
            if element == None:
                element = {"tagname": tagname}
        elif tagname != "result":
            raise Exception("Invalid root element: '%s'" % tagname)
        else:
            element = IbisResult(attrs)
            self.result = element
        self.node_stack.append(element)

    def end_element(self, tagname):
        if self.node_stack:
            element = self.node_stack[-1]
            self.node_stack.pop()
            if self.node_stack:
                parent = self.node_stack[-1]
                if isinstance(parent, list):
                    if isinstance(element, dict):
                        parent.append(element.get("data"))
                    else:
                        parent.append(element)
                elif not isinstance(parent, dict):
                    if isinstance(element, dict):
                        data = element.get("data")
                    else:
                        data = element
                    parent.end_child_element(tagname, data)
        else:
            raise Exception("Unexpected closing tag: '%s'" % tagname)

    def char_data(self, data):
        if self.node_stack:
            element = self.node_stack[-1]
            if isinstance(element, IbisIdentifier):
                if element.value != None: element.value += data
                else: element.value = data
            elif isinstance(element, dict):
                if "data" in element: element["data"] += data
                else: element["data"] = data

    def parse_xml(self, data):
        """
        Parse XML data from the specified string and return an IbisResult.

        **Parameters**
          `data` : str
            [required] The XML string returned from the server.

        **Returns**
          :any:`IbisResult`
            The parsed results. This may contain lists or trees of objects
            representing people, institutions and groups returned from the
            server.
        """
        self.parser.Parse(data)
        return self.result.unflatten()

    def parse_xml_file(self, file):
        """
        Parse XML data from the specified file and return an IbisResult.

        **Parameters**
          `file` : file
            [required] A file object containing XML returned from the server.

        **Returns**
          :any:`IbisResult`
            The parsed results. This may contain lists or trees of objects
            representing people, institutions and groups returned from the
            server.
        """
        self.parser.ParseFile(file)
        return self.result.unflatten()
