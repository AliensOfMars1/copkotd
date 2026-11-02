class Role:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    FINANCIAL_OFFICER = "financial_officer"
    RECORDS_OFFICER = "records_officer"
    COMPLIANCE_OFFICER = "compliance_officer"
    DATA_OFFICER = "data_officer"
    COMMUNICATIONS_OFFICER = "communications_officer"
    PROGRAMS_OFFICER = "programs_officer"
    MINISTRY_LEADER = "ministry_leader"

    ALL = [
        SUPER_ADMIN, ADMIN, FINANCIAL_OFFICER, RECORDS_OFFICER,
        COMPLIANCE_OFFICER, DATA_OFFICER, COMMUNICATIONS_OFFICER,
        PROGRAMS_OFFICER, MINISTRY_LEADER,
    ]

    LABELS = {
        SUPER_ADMIN: "Super Admin",
        ADMIN: "Admin",
        FINANCIAL_OFFICER: "Financial Officer",
        RECORDS_OFFICER: "Records Officer",
        COMPLIANCE_OFFICER: "Compliance Officer",
        DATA_OFFICER: "Data Officer",
        COMMUNICATIONS_OFFICER: "Communications Officer",
        PROGRAMS_OFFICER: "Programs Officer",
        MINISTRY_LEADER: "Ministry Leader",
    }