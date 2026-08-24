import streamlit as st
import pandas as pd

from agent import ask_agent



# PAGE CONFIGUR


st.set_page_config(
    page_title="ParcelPilot AI",
    
    layout="wide"
)



# DEMO USERS


USERS = {

    "support@parcelpilot.com": {
        "password": "support123",
        "role": "support"
    },

    "manager@parcelpilot.com": {
        "password": "manager123",
        "role": "manager"
    }

}


# SESSION STATE


if "authenticated" not in st.session_state:

    st.session_state.authenticated = False


if "messages" not in st.session_state:

    st.session_state.messages = []


# LOGIN PAGE


if not st.session_state.authenticated:

    st.title("ParcelPilot AI")

    st.subheader("Internal Support Assistant")

    st.write(
        "Secure AI assistant for authorised "
        "ParcelPilot support and operations staff."
    )

    st.divider()

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        st.markdown(
            "###  Staff Login"
        )

        email = st.text_input(
            "Email",
            placeholder="Enter your ParcelPilot email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        login = st.button(
            "Login",
            use_container_width=True
        )

        if login:

            user = USERS.get(email)

            if (
                user
                and user["password"] == password
            ):

                st.session_state.authenticated = True

                st.session_state.user_email = email

                st.session_state.user_role = user["role"]

                st.session_state.messages = []

                st.rerun()

            else:

                st.error(
                    "Invalid email or password."
                )

    st.stop()



# CURRENT USER


user_role = st.session_state.user_role

user_email = st.session_state.user_email



# SIDEBAR


with st.sidebar:

    st.title(" ParcelPilot")

    st.success(
        "Authenticated"
    )

    st.write(
        f"**User:** {user_email}"
    )

    st.write(
        f"**Role:** {user_role.upper()}"
    )

    st.divider()


   
    # ACCESS INFORMATION
   

    st.markdown(
        "###  Access"
    )

    if user_role == "support":

        st.info(
            "Support access\n\n"
            "✓ Orders\n\n"
            "✓ Tickets\n\n"
            "✓ Policies\n\n"
            "✓ Customer agreements\n\n"
            "✗ Create escalations"
        )

    else:

        st.success(
            "Manager access\n\n"
            "✓ Orders\n\n"
            "✓ Tickets\n\n"
            "✓ Policies\n\n"
            "✓ Customer agreements\n\n"
            "✓ Create escalations"
        )


    st.divider()


 
    # AVAILABLE TOOLS
  

    st.markdown(
        "###  Available Tools"
    )

    st.write(
        " Document Search"
    )

    st.write(
        " Structured Data Lookup"
    )

    st.write(
        " Escalation Action"
    )


    st.divider()


   
    # APPLICATION NAVIGATION
  

    page = st.radio(
        "Application",
        [
            "Support Assistant",
            "Operations Dashboard"
        ]
    )


    st.divider()


  
    # LOGOUT
   

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.authenticated = False

        st.session_state.pop(
            "user_email",
            None
        )

        st.session_state.pop(
            "user_role",
            None
        )

        st.session_state.pop(
            "messages",
            None
        )

        st.rerun()



# LOAD OPERATIONS DATA


def load_operations_data():

    excel_file = "ParcelPilot_Assessment_Data.xlsx"


   
    # ORDERS
 

    try:

        orders = pd.read_excel(
            excel_file,
            sheet_name="orders"
        )

    except Exception:

        orders = pd.DataFrame()


    
    # TICKETS
 

    try:

        tickets = pd.read_excel(
            excel_file,
            sheet_name="tickets"
        )

    except Exception:

        tickets = pd.DataFrame()


    return orders, tickets



# PROACTIVE ISSUE DETECTION


def detect_issues():

    orders, tickets = load_operations_data()

    issues = []


  
    # ORDER ISSUES
   

    if not orders.empty:


       
        # CARRIER FAULT
       

        if "carrier_fault" in orders.columns:

            carrier_faults = orders[
                orders["carrier_fault"]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "true",
                        "1",
                        "yes"
                    ]
                )
            ]

            if len(carrier_faults) > 0:

                issues.append(
                    {
                        "type": "Carrier Fault",
                        "severity": "High",
                        "count": len(carrier_faults),
                        "description":
                            f"{len(carrier_faults)} "
                            "order(s) are marked "
                            "as carrier fault."
                    }
                )


       
        # CUSTOMER FAULT
  

        if "customer_fault" in orders.columns:

            customer_faults = orders[
                orders["customer_fault"]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "true",
                        "1",
                        "yes"
                    ]
                )
            ]

            if len(customer_faults) > 0:

                issues.append(
                    {
                        "type": "Customer Fault",
                        "severity": "Medium",
                        "count": len(customer_faults),
                        "description":
                            f"{len(customer_faults)} "
                            "order(s) are marked "
                            "as customer fault."
                    }
                )


        # BOOKED BUT NOT PICKED UP
       

        if (
            "status" in orders.columns
            and
            "pickup_actual_at" in orders.columns
        ):

            booked_not_picked = orders[
                (
                    orders["status"]
                    .astype(str)
                    .str.upper()
                    == "BOOKED"
                )
                &
                (
                    orders["pickup_actual_at"]
                    .isna()
                )
            ]

            if len(booked_not_picked) > 0:

                issues.append(
                    {
                        "type": "Pickup Pending",
                        "severity": "Medium",
                        "count": len(booked_not_picked),
                        "description":
                            f"{len(booked_not_picked)} "
                            "booked shipment(s) "
                            "have not been picked up."
                    }
                )


 
    # TICKET ISSUES
   

    if not tickets.empty:


       
        # FIND PRIORITY COLUMN
       
        priority_column = None

        for column in tickets.columns:

            if column.lower() in {
                "priority",
                "priority_level",
                "severity"
            }:

                priority_column = column

                break


       
        # CRITICAL TICKETS
     
        if priority_column:

            priority_values = (
                tickets[priority_column]
                .astype(str)
                .str.upper()
            )

            critical = tickets[
                priority_values.isin(
                    [
                        "P1",
                        "CRITICAL",
                        "1"
                    ]
                )
            ]

            if len(critical) > 0:

                issues.append(
                    {
                        "type": "Critical Tickets",
                        "severity": "Critical",
                        "count": len(critical),
                        "description":
                            f"{len(critical)} "
                            "critical ticket(s) "
                            "require attention."
                    }
                )


    return issues



# SUPPORT ASSISTANT


if page == "Support Assistant":


   
    # HEADER
 

    st.title(
        "ParcelPilot AI Support"
    )

    st.caption(
        "AI-powered support assistant for "
        "authorised ParcelPilot staff"
    )


    
    # WELCOME MESSAGE


    if not st.session_state.messages:

        st.info(
            "Ask questions about orders, tickets, "
            "accounts, policies, customer agreements, "
            "or operational issues."
        )

        st.markdown(
            "### Example Questions"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.markdown(
                """
                **Order Investigation**

                What is the status of ORD-1001?
                """
            )


        with col2:

            st.markdown(
                """
                **Policy Investigation**

                Can Northstar cancel ORD-1001
                without a cancellation fee?
                """
            )


        with col3:

            st.markdown(
                """
                **⚡ Escalation**

                Prepare an escalation for
                ticket TKT-501.
                """
            )


  
    # CHAT HISTORY
  

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


   
    # CHAT INPUT


    question = st.chat_input(
        "Ask about an order, account, ticket, or policy..."
    )


    if question:


       
        # USER MESSAGE
    

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        with st.chat_message("user"):

            st.markdown(
                question
            )


       
        # AGENT RESPONSE
       

        with st.chat_message("assistant"):

            status = st.empty()

            status.info(
                "🔎 Investigating your request..."
            )


            with st.spinner(
                "Agent is working..."
            ):

                try:

                    result = ask_agent(
                        question=question,
                        chat_history=
                            st.session_state.messages[:-1],
                        user_role=user_role
                    )


                    content = result[
                        "messages"
                    ][-1].content


                   
                    # CLEAN RESPONSE
                  

                    if isinstance(
                        content,
                        list
                    ):

                        answer = "\n".join(
                            item.get(
                                "text",
                                ""
                            )
                            for item in content
                            if (
                                isinstance(
                                    item,
                                    dict
                                )
                                and
                                item.get(
                                    "type"
                                ) == "text"
                            )
                        )

                    else:

                        answer = str(
                            content
                        )


                    status.empty()


                    st.markdown(
                        answer
                    )


                except Exception as e:

                    status.empty()

                    answer = (
                        "Sorry, I was unable "
                        "to process your request. "
                        "Please try again."
                    )

                    st.error(
                        answer
                    )

                    print(
                        "Agent error:",
                        e
                    )


       
        # SAVE RESPONSE
      

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )



# OPERATIONS DASHBOARD

if page == "Operations Dashboard":


   
    # HEADER
   

    st.title(
        "ParcelPilot Operations"
    )

    st.caption(
        "Proactive issue detection for authorised "
        "support and operations staff."
    )

    st.divider()


   
    # LOAD DATA
   

    orders, tickets = (
        load_operations_data()
    )


   
    # DETECT ISSUES


    issues = detect_issues()

    # KPI CARDS
   

    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Total Orders",
            len(orders)
        )


    with col2:

        st.metric(
            "Total Tickets",
            len(tickets)
        )


    with col3:

        if (
            not orders.empty
            and
            "carrier_fault"
            in orders.columns
        ):

            carrier_fault_count = (
                orders[
                    "carrier_fault"
                ]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "true",
                        "1",
                        "yes"
                    ]
                )
                .sum()
            )

        else:

            carrier_fault_count = 0


        st.metric(
            "Carrier Faults",
            carrier_fault_count
        )


    with col4:

        st.metric(
            "Issues Detected",
            len(issues)
        )

    # ISSUE DETECTION
    

    st.divider()

    st.subheader(
        " Issues Requiring Attention"
    )


    if not issues:

        st.success(
            "No significant issues detected."
        )


    else:

        for issue in issues:

            severity = issue[
                "severity"
            ]


            if severity == "Critical":

                st.error(
                    f" **{issue['type']}** — "
                    f"{issue['description']}"
                )


            elif severity == "High":

                st.warning(
                    f" **{issue['type']}** — "
                    f"{issue['description']}"
                )


            else:

                st.info(
                    f" **{issue['type']}** — "
                    f"{issue['description']}"
                )


  
    # CARRIER FAULT ORDERS
   

    st.divider()

    st.subheader(
        "Carrier Fault Orders"
    )


    if (
        not orders.empty
        and
        "carrier_fault"
        in orders.columns
    ):

        carrier_fault_orders = orders[
            orders["carrier_fault"]
            .astype(str)
            .str.lower()
            .isin(
                [
                    "true",
                    "1",
                    "yes"
                ]
            )
        ]


        if not carrier_fault_orders.empty:

            st.dataframe(
                carrier_fault_orders,
                use_container_width=True
            )

        else:

            st.success(
                "No carrier-fault orders detected."
            )


   
    # PENDING PICKUPS
   

    st.divider()

    st.subheader(
        " Booked Shipments Awaiting Pickup"
    )


    if (
        not orders.empty
        and
        "status"
        in orders.columns
        and
        "pickup_actual_at"
        in orders.columns
    ):

        pending_pickups = orders[
            (
                orders["status"]
                .astype(str)
                .str.upper()
                == "BOOKED"
            )
            &
            orders[
                "pickup_actual_at"
            ].isna()
        ]


        if not pending_pickups.empty:

            st.dataframe(
                pending_pickups,
                use_container_width=True
            )

        else:

            st.success(
                "No booked shipments are currently "
                "awaiting pickup."
            )


    
    # TICKETS TABLE
  

    st.divider()

    st.subheader(
        " Critical / High Priority Tickets"
    )


    if not tickets.empty:

        priority_column = None


        for column in tickets.columns:

            if column.lower() in {
                "priority",
                "priority_level",
                "severity"
            }:

                priority_column = column

                break


        if priority_column:

            priority_values = (
                tickets[
                    priority_column
                ]
                .astype(str)
                .str.upper()
            )


            important_tickets = tickets[
                priority_values.isin(
                    [
                        "P1",
                        "P2",
                        "CRITICAL",
                        "HIGH",
                        "1",
                        "2"
                    ]
                )
            ]


            if not important_tickets.empty:

                st.dataframe(
                    important_tickets,
                    use_container_width=True
                )

            else:

                st.success(
                    "No critical or high-priority "
                    "tickets detected."
                )

        else:

            st.info(
                "No priority column was found "
                "in the tickets data."
            )

    else:

        st.info(
            "No ticket data available."
        )
