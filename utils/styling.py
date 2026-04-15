"""Pandas DataFrame stylers."""
import pandas as pd


def style_status_df(df: pd.DataFrame) -> pd.DataFrame.style:
    """Style status DataFrame with colors."""
    def color_status(val):
        colors = {
            "available": "color: #2ecc71",
            "dispatched": "color: #f39c12",
            "returning": "color: #3498db",
            "en_route": "color: #f39c12",
            "arrived": "color: #9b59b6",
            "rescued": "color: #2ecc71",
            "complete": "color: #2ecc71"
        }
        return colors.get(str(val).lower(), "")
    
    def color_fuel(val):
        try:
            pct = float(val)
            if pct < 20:
                return "color: #e74c3c; font-weight: bold"
            elif pct < 50:
                return "color: #f39c12"
            return "color: #2ecc71"
        except:
            return ""
    
    styled = df.style
    if 'status' in df.columns:
        styled = styled.map(color_status, subset=['status'])
    if 'fuel_pct' in df.columns:
        styled = styled.map(color_fuel, subset=['fuel_pct'])
    
    return styled


def style_algorithm_comparison(df: pd.DataFrame) -> pd.DataFrame.style:
    """Style algorithm comparison table."""
    def highlight_recommended(row):
        if row.get('recommended'):
            return ['background-color: #2d6a4f'] * len(row)
        return [''] * len(row)
    
    def color_found(val):
        if val == True or str(val).lower() == 'true':
            return "color: #2ecc71"
        elif val == False or str(val).lower() == 'false':
            return "color: #e74c3c"
        return ""
    
    styled = df.style
    if 'found' in df.columns:
        styled = styled.map(color_found, subset=['found'])
    
    # Highlight recommended row
    styled = styled.apply(highlight_recommended, axis=1)
    
    return styled


def style_disaster_events(df: pd.DataFrame) -> pd.DataFrame.style:
    """Style disaster events table."""
    def color_injury(val):
        colors = {
            "critical": "color: #e74c3c; font-weight: bold",
            "high": "color: #e67e22",
            "medium": "color: #f39c12",
            "low": "color: #f1c40f",
            "none": "color: #95a5a6"
        }
        return colors.get(str(val).lower(), "")
    
    def color_survival(val):
        try:
            pct = float(val)
            if pct < 0.3:
                return "color: #e74c3c; font-weight: bold"
            elif pct < 0.6:
                return "color: #f39c12"
            return "color: #2ecc71"
        except:
            return ""
    
    styled = df.style
    if 'injury_level' in df.columns:
        styled = styled.map(color_injury, subset=['injury_level'])
    if 'survival_chance' in df.columns:
        styled = styled.map(color_survival, subset=['survival_chance'])
    
    return styled


def style_knapsack_result(df: pd.DataFrame, selected_indices: list) -> pd.DataFrame.style:
    """Style knapsack result with selected items highlighted."""
    def highlight_selected(row):
        if row.name in selected_indices:
            return ['background-color: #2d6a4f'] * len(row)
        return ['background-color: #333333'] * len(row)
    
    return df.style.apply(highlight_selected, axis=1)


def style_teams_df(df: pd.DataFrame) -> pd.DataFrame.style:
    """Style teams DataFrame."""
    def color_status(val):
        colors = {
            "available": "color: #2ecc71",
            "dispatched": "color: #f39c12",
            "returning": "color: #3498db"
        }
        return colors.get(str(val).lower(), "")
    
    def color_fuel(val):
        try:
            pct = float(val)
            if pct < 20:
                return "background-color: rgba(231, 76, 60, 0.3); color: #e74c3c"
        except:
            pass
        return ""
    
    styled = df.style
    if 'status' in df.columns:
        styled = styled.map(color_status, subset=['status'])
    if 'fuel_pct' in df.columns:
        styled = styled.map(color_fuel, subset=['fuel_pct'])
    
    return styled
