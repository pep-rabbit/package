import polars as pl


async def get_top_pharmacies(city: str, medical_program: str) -> pl.DataFrame:
    return await (
        pl.scan_csv("src/data/reimbursement_legal_entity_divisions_info.csv")
        .with_columns(
            pl.col("medical_programs_in_divisions")
            .str.extract_all(r'"[^"]+"|[^,{}]+')
            .list.eval(
                pl.element().str.strip_chars().str.strip_chars('"'), parallel=True
            ),
        )
        .cache()
        .filter(pl.col("division_settlement").str.to_lowercase() == city.lower())
        .join(
            (
                pl.scan_csv("src/data/payments_on_contracts_pharmacy_2025.csv")
                .group_by("legal_entity_edrpou")
                .agg(pl.col("pay_all").sum().alias("activity_score"))
                .cache()
            ),
            on="legal_entity_edrpou",
            how="inner",
        )
        .filter(
            pl.col("medical_programs_in_divisions")
            .list.eval(
                pl.element().str.contains(medical_program, literal=True),
                parallel=True,
            )
            .list.any()
        )
        .select(
            [
                "legal_entity_name",
                "division_name",
                "division_addresses",
                "division_phone",
                "division_type",
                "division_settlement",
                "activity_score",
            ]
        )
        .sort("activity_score", descending=True)
        .head(5)
    ).collect_async()
