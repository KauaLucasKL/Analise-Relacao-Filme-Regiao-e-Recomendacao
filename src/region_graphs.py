def filter_region_exact(df, region_countries):
    """
    Mantém apenas países pertencentes à região,
    mesmo em casos de coprodução.
    """
    df = df.copy()

    def keep_region_only(country_field):
        countries = [c.strip() for c in country_field.split(',') if c.strip()]
        region_only = [c for c in countries if c in region_countries]
        return ', '.join(region_only)

    df['country'] = df['country'].apply(keep_region_only)

    # Remove filmes que não ficaram com países da região
    df = df[df['country'] != '']

    return df
