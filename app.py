import streamlit as st
import pandas as pd

from agent import (
    create_client,
    analyze_prescription
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Prescription-to-Life",
    page_icon="💊",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("💊 Prescription-to-Life")

st.write(
    "AI-powered prescription understanding "
    "and medicine scheduling."
)

st.info(
    "Upload a clear prescription image. "
    "If important information cannot be read reliably, "
    "the AI will stop instead of guessing."
)


# =========================================================
# LANGUAGE
# =========================================================

language = st.selectbox(
    "Select Language / زبان منتخب کریں",
    [
        "English",
        "Urdu"
    ]
)


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "Upload Prescription",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


# =========================================================
# MAIN APP
# =========================================================

if uploaded_file:

    st.subheader(
        "📷 Uploaded Prescription"
    )

    st.image(
        uploaded_file,
        width=600
    )


    if st.button(
        "🔍 Analyze Prescription",
        type="primary"
    ):

        try:

            # ---------------------------------------------
            # API KEY
            # ---------------------------------------------

            api_key = st.secrets[
                "GROQ_API_KEY"
            ]


            # ---------------------------------------------
            # CLIENT
            # ---------------------------------------------

            client = create_client(
                api_key
            )


            # ---------------------------------------------
            # IMAGE
            # ---------------------------------------------

            image_bytes = (
                uploaded_file.getvalue()
            )

            mime_type = uploaded_file.type


            # ---------------------------------------------
            # RUN AGENTS
            # ---------------------------------------------

            with st.spinner(
                "AI agents are analyzing the prescription..."
            ):

                result = analyze_prescription(
                    client=client,
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    language=language
                )


            # =================================================
            # SAFETY FAILURE
            # =================================================

            if not result["success"]:

                st.error(
                    "⚠️ The prescription could not "
                    "be reliably verified."
                )

                verification = result.get(
                    "verification",
                    {}
                )

                warning = verification.get(
                    "warning",
                    "Some information is unclear."
                )

                st.warning(
                    warning
                )

                st.info(
                    "Please upload a clearer prescription "
                    "or confirm the unclear information "
                    "with a doctor or pharmacist."
                )

                st.stop()


            # =================================================
            # SUCCESS
            # =================================================

            st.success(
                "✅ Prescription processed successfully."
            )


            final_data = result.get(
                "final",
                {}
            )


            # =================================================
            # MEDICINE TABLE
            # =================================================

            st.subheader(
                "💊 Medicine Schedule"
            )

            schedule = final_data.get(
                "schedule",
                []
            )


            if schedule:

                df = pd.DataFrame(
                    schedule
                )

                # Rename columns for friendly UI

                df = df.rename(
                    columns={
                        "medicine_name": "Medicine",
                        "dosage": "Dosage",
                        "frequency": "Frequency",
                        "morning": "Morning",
                        "afternoon": "Afternoon",
                        "evening": "Evening",
                        "night": "Night",
                        "duration": "Duration"
                    }
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    "No schedule information was found."
                )


            # =================================================
            # SIMPLE MEDICINE USE
            # =================================================

            st.subheader(
                "📖 Simple Medicine Explanation"
            )

            explanations = final_data.get(
                "explanations",
                []
            )


            if explanations:

                for item in explanations:

                    medicine = item.get(
                        "medicine_name",
                        "Medicine"
                    )

                    simple_use = item.get(
                        "simple_use",
                        "Purpose could not be safely determined."
                    )

                    st.markdown(
                        f"### 💊 {medicine}"
                    )

                    st.write(
                        simple_use
                    )

            else:

                st.write(
                    "No explanation available."
                )


            # =================================================
            # SAFETY NOTICE
            # =================================================

            st.divider()

            st.warning(
                "⚠️ This application provides AI-assisted "
                "information and does not replace a doctor "
                "or pharmacist. Confirm unclear information "
                "with a qualified healthcare professional."
            )


        except Exception as error:

            st.error(
                "❌ An error occurred while analyzing "
                "the prescription."
            )

            st.code(
                str(error)
)
