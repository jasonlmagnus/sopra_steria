#!/usr/bin/env python3
"""
DASHBOARD INTEGRITY AUDIT
Systematic analysis of ALL styling inconsistencies across dashboard pages
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class DashboardStyleAuditor:
    def __init__(self):
        self.dashboard_dir = Path("audit_tool/dashboard/pages")
        self.issues = defaultdict(list)
        self.font_sizes = set()
        self.font_weights = set()
        self.font_families = set()
        self.css_classes = set()
        self.inline_styles = []
        
        # Chart styling tracking
        self.chart_heights = set()
        self.chart_colors = set()
        self.chart_templates = set()
        self.chart_issues = defaultdict(list)
        
        # Table styling tracking
        self.table_fonts = set()
        self.table_issues = defaultdict(list)
        
        # Key metrics tracking
        self.metric_styles = set()
        self.metric_issues = defaultdict(list)
        
        # Card component tracking
        self.card_styles = set()
        self.card_issues = defaultdict(list)
        
        # Filter widget tracking
        self.filter_styles = set()
        self.filter_issues = defaultdict(list)
        
        # RAG (Red/Amber/Green) tracking
        self.rag_colors = set()
        self.rag_styles = set()
        self.rag_issues = defaultdict(list)
        
        # Button styling tracking
        self.button_styles = set()
        self.button_issues = defaultdict(list)
        
        # Badge/Tag styling tracking
        self.badge_styles = set()
        self.badge_issues = defaultdict(list)
        
        # Icon styling tracking
        self.icon_styles = set()
        self.icon_issues = defaultdict(list)
        
        # Alert/Notification styling tracking
        self.alert_styles = set()
        self.alert_issues = defaultdict(list)
        
        # Layout styling tracking
        self.layout_styles = set()
        self.layout_issues = defaultdict(list)
        
        # Spacing/Margin tracking
        self.spacing_styles = set()
        self.spacing_issues = defaultdict(list)
        
        # Border styling tracking
        self.border_styles = set()
        self.border_issues = defaultdict(list)
        
        # Animation/Transition tracking
        self.animation_styles = set()
        self.animation_issues = defaultdict(list)
        
        # Tooltip/Help tracking
        self.tooltip_styles = set()
        self.tooltip_issues = defaultdict(list)
        
        # Progress/Loading tracking
        self.progress_styles = set()
        self.progress_issues = defaultdict(list)
        
        # Tab/Expander tracking
        self.tab_styles = set()
        self.tab_issues = defaultdict(list)
        
        # Sidebar/Column tracking
        self.sidebar_styles = set()
        self.sidebar_issues = defaultdict(list)
        
    def audit_all_pages(self):
        """Audit all dashboard pages for styling issues"""
        print("🔍 COMPREHENSIVE DASHBOARD STYLING AUDIT")
        print("=" * 60)
        
        pages = list(self.dashboard_dir.glob("*.py"))
        
        for page_path in pages:
            if page_path.name.startswith("__"):
                continue
                
            print(f"\n📄 Auditing: {page_path.name}")
            self.audit_page(page_path)
        
        self.generate_report()
    
    def audit_page(self, page_path):
        """Audit a single page for styling issues"""
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        page_name = page_path.name
        
        # Find inline styles
        inline_patterns = [
            r'style="([^"]*)"',
            r"style='([^']*)'",
        ]
        
        for pattern in inline_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                self.inline_styles.append({
                    'page': page_name,
                    'style': match,
                    'line': self._find_line_number(content, match)
                })
        
        # Find font sizes
        font_size_matches = re.findall(r'font-size:\s*([^;"\s]+)', content)
        for size in font_size_matches:
            self.font_sizes.add(size)
            self.issues[page_name].append(f"Font size: {size}")
        
        # Find font weights
        font_weight_matches = re.findall(r'font-weight:\s*([^;"\s]+)', content)
        for weight in font_weight_matches:
            self.font_weights.add(weight)
            self.issues[page_name].append(f"Font weight: {weight}")
        
        # Find font families
        font_family_matches = re.findall(r'font-family:\s*([^;"}]+)', content)
        for family in font_family_matches:
            self.font_families.add(family.strip())
            self.issues[page_name].append(f"Font family: {family}")
        
        # Find CSS classes
        class_matches = re.findall(r'class="([^"]*)"', content)
        for classes in class_matches:
            for cls in classes.split():
                self.css_classes.add(cls)
        
        # Find header inconsistencies
        streamlit_headers = len(re.findall(r'st\.markdown\(["\']#+[^"\']*["\']', content))
        html_headers = len(re.findall(r'<h[1-6][^>]*>', content))
        
        if streamlit_headers > 0 and html_headers > 0:
            self.issues[page_name].append(f"Mixed headers: {streamlit_headers} Streamlit, {html_headers} HTML")
        
        # Find metric card inconsistencies
        metric_systems = []
        if 'metric-card' in content:
            metric_systems.append('brand-system')
        if 'metric-primary' in content:
            metric_systems.append('semantic-system')
        if 'st.metric(' in content:
            metric_systems.append('streamlit-system')
        
        if len(metric_systems) > 1:
            self.issues[page_name].append(f"Multiple metric systems: {', '.join(metric_systems)}")
        
        # ALL STYLING AUDITS
        self.audit_chart_styling(page_name, content)
        self.audit_table_styling(page_name, content)
        self.audit_key_metrics(page_name, content)
        self.audit_card_components(page_name, content)
        self.audit_filter_widgets(page_name, content)
        self.audit_rag_styles(page_name, content)
        self.audit_button_styling(page_name, content)
        self.audit_badge_styling(page_name, content)
        self.audit_icon_styling(page_name, content)
        self.audit_alert_styling(page_name, content)
        self.audit_layout_styling(page_name, content)
        self.audit_spacing_styling(page_name, content)
        self.audit_border_styling(page_name, content)
        self.audit_animation_styling(page_name, content)
        self.audit_tooltip_styling(page_name, content)
        self.audit_progress_styling(page_name, content)
        self.audit_tab_styling(page_name, content)
        self.audit_sidebar_styling(page_name, content)
    
    def audit_chart_styling(self, page_name, content):
        """Audit chart styling inconsistencies"""
        
        # Chart heights
        height_matches = re.findall(r'height=(\d+)', content)
        for height in height_matches:
            self.chart_heights.add(height)
            self.chart_issues[page_name].append(f"Chart height: {height}px")
        
        # Chart layout heights
        layout_height_matches = re.findall(r'update_layout\([^)]*height=(\d+)', content)
        for height in layout_height_matches:
            self.chart_heights.add(height)
            self.chart_issues[page_name].append(f"Layout height: {height}px")
        
        # Chart colors - discrete sequences
        color_discrete_matches = re.findall(r'color_discrete_sequence=\[([^\]]+)\]', content)
        for colors in color_discrete_matches:
            self.chart_colors.add(colors.strip())
            self.chart_issues[page_name].append(f"Discrete colors: {colors[:50]}...")
        
        # Chart colors - continuous scales
        color_continuous_matches = re.findall(r'color_continuous_scale=["\']([^"\']+)["\']', content)
        for scale in color_continuous_matches:
            self.chart_colors.add(scale)
            self.chart_issues[page_name].append(f"Color scale: {scale}")
        
        # Chart templates
        template_matches = re.findall(r'template=["\']([^"\']+)["\']', content)
        for template in template_matches:
            self.chart_templates.add(template)
            self.chart_issues[page_name].append(f"Chart template: {template}")
        
        # Chart font styling
        chart_font_matches = re.findall(r'font=dict\(([^)]+)\)', content)
        for font_config in chart_font_matches:
            self.chart_issues[page_name].append(f"Chart font config: {font_config[:50]}...")
        
        # Chart title fonts
        title_font_matches = re.findall(r'title_font=dict\(([^)]+)\)', content)
        for title_font in title_font_matches:
            self.chart_issues[page_name].append(f"Chart title font: {title_font[:50]}...")
        
        # Plotly color usage
        plotly_color_matches = re.findall(r'px\.colors\.([^,\s)]+)', content)
        for color_ref in plotly_color_matches:
            self.chart_colors.add(f"px.colors.{color_ref}")
            self.chart_issues[page_name].append(f"Plotly color: px.colors.{color_ref}")
        
        # Chart type inconsistencies
        chart_types = []
        if 'px.bar(' in content:
            chart_types.append('px.bar')
        if 'px.pie(' in content:
            chart_types.append('px.pie')
        if 'px.histogram(' in content:
            chart_types.append('px.histogram')
        if 'px.scatter(' in content:
            chart_types.append('px.scatter')
        if 'px.imshow(' in content:
            chart_types.append('px.imshow')
        if 'go.Figure(' in content:
            chart_types.append('go.Figure')
        if 'go.Bar(' in content:
            chart_types.append('go.Bar')
        if 'go.Scatter(' in content:
            chart_types.append('go.Scatter')
        
        if len(chart_types) > 2:
            self.chart_issues[page_name].append(f"Multiple chart types: {', '.join(chart_types)}")
    
    def audit_table_styling(self, page_name, content):
        """Audit table and dataframe styling inconsistencies"""
        
        # DataFrame styling
        if 'st.dataframe(' in content:
            self.table_issues[page_name].append("Uses st.dataframe")
        
        if 'st.table(' in content:
            self.table_issues[page_name].append("Uses st.table")
        
        # Styled DataFrames
        styled_df_matches = re.findall(r'\.style\.([^(]+)\(', content)
        for style_method in styled_df_matches:
            self.table_issues[page_name].append(f"DataFrame style: .style.{style_method}")
        
        # Table font formatting
        table_font_matches = re.findall(r'format\(\{[^}]*font[^}]*\}\)', content)
        for font_format in table_font_matches:
            self.table_fonts.add(font_format[:50])
            self.table_issues[page_name].append(f"Table font format: {font_format[:50]}...")
        
        # Background gradient usage
        if '.background_gradient(' in content:
            self.table_issues[page_name].append("Uses background_gradient styling")
        
        # Custom table styling
        if 'use_container_width=True' in content:
            self.table_issues[page_name].append("Uses container width")
        
        if 'use_container_width=False' in content:
            self.table_issues[page_name].append("Fixed width tables")
    
    def audit_key_metrics(self, page_name, content):
        """Audit key metrics styling inconsistencies"""
        
        # st.metric usage
        metric_matches = re.findall(r'st\.metric\([^)]+\)', content)
        for metric in metric_matches:
            self.metric_styles.add("st.metric")
            self.metric_issues[page_name].append(f"Streamlit metric: {metric[:50]}...")
        
        # Custom metric cards
        if 'metric-card' in content:
            self.metric_styles.add("metric-card")
            self.metric_issues[page_name].append("Uses metric-card class")
        
        if 'metric-value' in content:
            self.metric_styles.add("metric-value")
            self.metric_issues[page_name].append("Uses metric-value class")
        
        if 'metric-label' in content:
            self.metric_styles.add("metric-label")
            self.metric_issues[page_name].append("Uses metric-label class")
        
        # Metric delta styling
        delta_matches = re.findall(r'delta=["\']([^"\']+)["\']', content)
        for delta in delta_matches:
            self.metric_issues[page_name].append(f"Metric delta: {delta}")
        
        # Custom metric styling
        custom_metric_matches = re.findall(r'<div[^>]*metric[^>]*>', content)
        for custom_metric in custom_metric_matches:
            self.metric_styles.add("custom-div-metric")
            self.metric_issues[page_name].append(f"Custom metric div: {custom_metric[:50]}...")
        
        # Metric color usage
        metric_color_matches = re.findall(r'delta_color=["\']([^"\']+)["\']', content)
        for color in metric_color_matches:
            self.metric_issues[page_name].append(f"Metric color: {color}")
    
    def audit_card_components(self, page_name, content):
        """Audit card component styling inconsistencies"""
        
        # Different card classes
        card_classes = [
            'metric-card', 'content-card', 'brand-card', 'status-card',
            'success-card', 'opportunity-card', 'pattern-card', 'insights-box'
        ]
        
        for card_class in card_classes:
            if card_class in content:
                self.card_styles.add(card_class)
                self.card_issues[page_name].append(f"Uses {card_class} class")
        
        # Custom card divs
        card_div_matches = re.findall(r'<div[^>]*card[^>]*>', content)
        for card_div in card_div_matches:
            self.card_styles.add("custom-card-div")
            self.card_issues[page_name].append(f"Custom card div: {card_div[:50]}...")
        
        # Streamlit containers as cards
        if 'st.container(' in content:
            self.card_issues[page_name].append("Uses st.container as card")
        
        # Card border styling
        border_matches = re.findall(r'border[^;]*:[^;]*;', content)
        for border in border_matches:
            if 'card' in content:
                self.card_issues[page_name].append(f"Card border: {border}")
        
        # Card background styling
        bg_matches = re.findall(r'background[^;]*:[^;]*;', content)
        for bg in bg_matches:
            if 'card' in content:
                self.card_issues[page_name].append(f"Card background: {bg[:50]}...")
    
    def audit_filter_widgets(self, page_name, content):
        """Audit filter widget styling inconsistencies"""
        
        # Streamlit filter widgets
        filter_widgets = [
            'st.selectbox', 'st.multiselect', 'st.slider', 'st.select_slider',
            'st.radio', 'st.checkbox', 'st.date_input', 'st.time_input'
        ]
        
        for widget in filter_widgets:
            if widget in content:
                self.filter_styles.add(widget)
                widget_matches = re.findall(rf'{widget}\([^)]+\)', content)
                for match in widget_matches:
                    self.filter_issues[page_name].append(f"Filter widget: {widget}")
        
        # Custom filter styling
        filter_style_matches = re.findall(r'<div[^>]*filter[^>]*>', content)
        for filter_style in filter_style_matches:
            self.filter_styles.add("custom-filter-div")
            self.filter_issues[page_name].append(f"Custom filter: {filter_style[:50]}...")
        
        # Filter container styling
        if 'st.sidebar' in content:
            self.filter_issues[page_name].append("Uses sidebar for filters")
        
        if 'st.columns(' in content:
            columns_matches = re.findall(r'st\.columns\((\d+)\)', content)
            for cols in columns_matches:
                self.filter_issues[page_name].append(f"Uses {cols} columns for layout")
    
    def audit_rag_styles(self, page_name, content):
        """Audit Red/Amber/Green (RAG) styling inconsistencies"""
        
        # RAG color definitions
        rag_color_patterns = [
            r'--status-excellent[^;]*:[^;]*;',
            r'--status-good[^;]*:[^;]*;',
            r'--status-warning[^;]*:[^;]*;',
            r'--status-critical[^;]*:[^;]*;',
            r'color.*red', r'color.*green', r'color.*amber', r'color.*orange',
            r'#[0-9a-fA-F]{6}.*red', r'#[0-9a-fA-F]{6}.*green'
        ]
        
        for pattern in rag_color_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                self.rag_colors.add(match)
                self.rag_issues[page_name].append(f"RAG color: {match[:50]}...")
        
        # RAG status classes
        rag_classes = [
            'status-excellent', 'status-good', 'status-warning', 'status-critical',
            'success', 'warning', 'error', 'critical', 'excellent', 'good',
            'priority-urgent', 'priority-high', 'priority-medium',
            'impact-high', 'impact-medium', 'performance-excellent'
        ]
        
        for rag_class in rag_classes:
            if rag_class in content:
                self.rag_styles.add(rag_class)
                self.rag_issues[page_name].append(f"RAG class: {rag_class}")
        
        # Custom RAG styling
        rag_inline_matches = re.findall(r'color:\s*[#\w]+[^;]*;', content)
        for color_style in rag_inline_matches:
            if any(color in color_style.lower() for color in ['red', 'green', 'orange', 'amber']):
                self.rag_issues[page_name].append(f"Inline RAG color: {color_style}")
        
        # Badge styling for RAG
        badge_matches = re.findall(r'["\']([^"\']*badge[^"\']*)["\']', content)
        for badge in badge_matches:
            if any(status in badge for status in ['critical', 'warning', 'success', 'excellent']):
                self.rag_styles.add(f"badge-{badge}")
                self.rag_issues[page_name].append(f"RAG badge: {badge}")
    
    def audit_button_styling(self, page_name, content):
        """Audit button styling inconsistencies"""
        
        # Streamlit buttons
        button_widgets = ['st.button', 'st.download_button', 'st.form_submit_button']
        
        for button in button_widgets:
            if button in content:
                self.button_styles.add(button)
                self.button_issues[page_name].append(f"Button widget: {button}")
        
        # Custom button classes
        button_classes = [
            'action-button', 'apply-button', 'copy-button', 'export-button',
            'primary-button', 'secondary-button', 'danger-button'
        ]
        
        for btn_class in button_classes:
            if btn_class in content:
                self.button_styles.add(btn_class)
                self.button_issues[page_name].append(f"Button class: {btn_class}")
        
        # Custom button divs
        button_div_matches = re.findall(r'<div[^>]*button[^>]*>', content)
        for button_div in button_div_matches:
            self.button_styles.add("custom-button-div")
            self.button_issues[page_name].append(f"Custom button: {button_div[:50]}...")
        
        # Button styling in CSS
        button_style_matches = re.findall(r'button[^{]*\{[^}]*\}', content)
        for button_style in button_style_matches:
            self.button_issues[page_name].append(f"Button CSS: {button_style[:50]}...")
    
    def audit_badge_styling(self, page_name, content):
        """Audit badge/tag styling inconsistencies"""
        
        # Badge classes
        badge_classes = [
            'badge', 'tag', 'chip', 'label', 'quick-win-badge', 'critical-badge',
            'metric-badge', 'status-badge', 'priority-badge'
        ]
        
        for badge_class in badge_classes:
            if badge_class in content:
                self.badge_styles.add(badge_class)
                self.badge_issues[page_name].append(f"Badge class: {badge_class}")
        
        # Custom badge styling
        badge_div_matches = re.findall(r'<span[^>]*badge[^>]*>', content)
        for badge_div in badge_div_matches:
            self.badge_styles.add("custom-badge-span")
            self.badge_issues[page_name].append(f"Custom badge: {badge_div[:50]}...")
    
    def audit_icon_styling(self, page_name, content):
        """Audit icon styling inconsistencies"""
        
        # Emoji icons
        emoji_matches = re.findall(r'[🔍🎯📊💡🌟📋🚀🎨👥🔬👤📄⚠️✅❌🔥💀🚨📈📉🎪🎭🎪]', content)
        for emoji in emoji_matches:
            self.icon_styles.add(f"emoji-{emoji}")
            self.icon_issues[page_name].append(f"Emoji icon: {emoji}")
        
        # Font awesome or other icon libraries
        icon_matches = re.findall(r'<i[^>]*class="[^"]*fa[^"]*"[^>]*>', content)
        for icon in icon_matches:
            self.icon_styles.add("font-awesome")
            self.icon_issues[page_name].append(f"Font Awesome: {icon[:50]}...")
        
        # Custom icon styling
        if 'icon' in content.lower():
            self.icon_issues[page_name].append("Contains icon references")
    
    def audit_alert_styling(self, page_name, content):
        """Audit alert/notification styling inconsistencies"""
        
        # Streamlit alerts
        alert_widgets = ['st.success', 'st.info', 'st.warning', 'st.error', 'st.exception']
        
        for alert in alert_widgets:
            if alert in content:
                self.alert_styles.add(alert)
                self.alert_issues[page_name].append(f"Alert widget: {alert}")
        
        # Custom alert classes
        alert_classes = ['alert', 'notification', 'message', 'toast', 'banner']
        
        for alert_class in alert_classes:
            if alert_class in content:
                self.alert_styles.add(alert_class)
                self.alert_issues[page_name].append(f"Alert class: {alert_class}")
        
        # Alert styling patterns
        if 'alert-' in content:
            self.alert_issues[page_name].append("Uses alert- prefix classes")
    
    def audit_layout_styling(self, page_name, content):
        """Audit layout styling inconsistencies"""
        
        # Streamlit layout elements
        layout_elements = [
            'st.columns', 'st.container', 'st.expander', 'st.tabs',
            'st.sidebar', 'st.empty', 'st.placeholder'
        ]
        
        for element in layout_elements:
            if element in content:
                self.layout_styles.add(element)
                self.layout_issues[page_name].append(f"Layout element: {element}")
        
        # CSS Grid/Flexbox
        if 'display: grid' in content:
            self.layout_styles.add("css-grid")
            self.layout_issues[page_name].append("Uses CSS Grid")
        
        if 'display: flex' in content:
            self.layout_styles.add("css-flexbox")
            self.layout_issues[page_name].append("Uses CSS Flexbox")
        
        # Layout classes
        layout_classes = [
            'container', 'row', 'col', 'grid', 'flex', 'wrapper',
            'section', 'panel', 'sidebar', 'main-content'
        ]
        
        for layout_class in layout_classes:
            if layout_class in content:
                self.layout_styles.add(layout_class)
                self.layout_issues[page_name].append(f"Layout class: {layout_class}")
    
    def audit_spacing_styling(self, page_name, content):
        """Audit spacing/margin/padding styling inconsistencies"""
        
        # Margin patterns
        margin_matches = re.findall(r'margin[^;]*:[^;]*;', content)
        for margin in margin_matches:
            self.spacing_styles.add(margin.strip())
            self.spacing_issues[page_name].append(f"Margin: {margin.strip()}")
        
        # Padding patterns
        padding_matches = re.findall(r'padding[^;]*:[^;]*;', content)
        for padding in padding_matches:
            self.spacing_styles.add(padding.strip())
            self.spacing_issues[page_name].append(f"Padding: {padding.strip()}")
        
        # Gap patterns
        gap_matches = re.findall(r'gap[^;]*:[^;]*;', content)
        for gap in gap_matches:
            self.spacing_styles.add(gap.strip())
            self.spacing_issues[page_name].append(f"Gap: {gap.strip()}")
    
    def audit_border_styling(self, page_name, content):
        """Audit border styling inconsistencies"""
        
        # Border patterns
        border_matches = re.findall(r'border[^;]*:[^;]*;', content)
        for border in border_matches:
            self.border_styles.add(border.strip())
            self.border_issues[page_name].append(f"Border: {border.strip()}")
        
        # Border radius patterns
        radius_matches = re.findall(r'border-radius[^;]*:[^;]*;', content)
        for radius in radius_matches:
            self.border_styles.add(radius.strip())
            self.border_issues[page_name].append(f"Border radius: {radius.strip()}")
        
        # Box shadow patterns
        shadow_matches = re.findall(r'box-shadow[^;]*:[^;]*;', content)
        for shadow in shadow_matches:
            self.border_styles.add(shadow.strip())
            self.border_issues[page_name].append(f"Box shadow: {shadow.strip()}")
    
    def audit_animation_styling(self, page_name, content):
        """Audit animation/transition styling inconsistencies"""
        
        # Animation patterns
        animation_matches = re.findall(r'animation[^;]*:[^;]*;', content)
        for animation in animation_matches:
            self.animation_styles.add(animation.strip())
            self.animation_issues[page_name].append(f"Animation: {animation.strip()}")
        
        # Transition patterns
        transition_matches = re.findall(r'transition[^;]*:[^;]*;', content)
        for transition in transition_matches:
            self.animation_styles.add(transition.strip())
            self.animation_issues[page_name].append(f"Transition: {transition.strip()}")
        
        # Transform patterns
        transform_matches = re.findall(r'transform[^;]*:[^;]*;', content)
        for transform in transform_matches:
            self.animation_styles.add(transform.strip())
            self.animation_issues[page_name].append(f"Transform: {transform.strip()}")
    
    def audit_tooltip_styling(self, page_name, content):
        """Audit tooltip/help styling inconsistencies"""
        
        # Streamlit help
        if 'help=' in content:
            self.tooltip_styles.add("streamlit-help")
            help_matches = re.findall(r'help=["\']([^"\']+)["\']', content)
            for help_text in help_matches:
                self.tooltip_issues[page_name].append(f"Help tooltip: {help_text[:30]}...")
        
        # Custom tooltip classes
        tooltip_classes = ['tooltip', 'help', 'hint', 'popover']
        
        for tooltip_class in tooltip_classes:
            if tooltip_class in content:
                self.tooltip_styles.add(tooltip_class)
                self.tooltip_issues[page_name].append(f"Tooltip class: {tooltip_class}")
    
    def audit_progress_styling(self, page_name, content):
        """Audit progress/loading styling inconsistencies"""
        
        # Streamlit progress elements
        progress_elements = ['st.progress', 'st.spinner', 'st.balloons', 'st.snow']
        
        for element in progress_elements:
            if element in content:
                self.progress_styles.add(element)
                self.progress_issues[page_name].append(f"Progress element: {element}")
        
        # Custom progress classes
        progress_classes = ['progress', 'progress-bar', 'loading', 'spinner']
        
        for progress_class in progress_classes:
            if progress_class in content:
                self.progress_styles.add(progress_class)
                self.progress_issues[page_name].append(f"Progress class: {progress_class}")
    
    def audit_tab_styling(self, page_name, content):
        """Audit tab/expander styling inconsistencies"""
        
        # Streamlit tabs and expanders
        if 'st.tabs(' in content:
            self.tab_styles.add("st.tabs")
            self.tab_issues[page_name].append("Uses st.tabs")
        
        if 'st.expander(' in content:
            self.tab_styles.add("st.expander")
            self.tab_issues[page_name].append("Uses st.expander")
        
        # Custom tab classes
        tab_classes = ['tab', 'tab-content', 'tab-pane', 'accordion', 'collapsible']
        
        for tab_class in tab_classes:
            if tab_class in content:
                self.tab_styles.add(tab_class)
                self.tab_issues[page_name].append(f"Tab class: {tab_class}")
    
    def audit_sidebar_styling(self, page_name, content):
        """Audit sidebar/column styling inconsistencies"""
        
        # Sidebar usage
        if 'st.sidebar' in content:
            self.sidebar_styles.add("st.sidebar")
            self.sidebar_issues[page_name].append("Uses st.sidebar")
        
        # Column layouts
        column_matches = re.findall(r'st\.columns\((\d+)\)', content)
        for cols in column_matches:
            self.sidebar_styles.add(f"columns-{cols}")
            self.sidebar_issues[page_name].append(f"Uses {cols} columns")
        
        # Custom sidebar classes
        sidebar_classes = ['sidebar', 'aside', 'navigation', 'menu']
        
        for sidebar_class in sidebar_classes:
            if sidebar_class in content:
                self.sidebar_styles.add(sidebar_class)
                self.sidebar_issues[page_name].append(f"Sidebar class: {sidebar_class}")
    
    def _find_line_number(self, content, search_text):
        """Find line number of text in content"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return None
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 100)
        print("🚨 COMPREHENSIVE DASHBOARD STYLING DISASTER REPORT")
        print("=" * 100)
        
        # Summary stats
        print(f"\n📊 COMPLETE CHAOS METRICS:")
        print(f"   • Font sizes found: {len(self.font_sizes)}")
        print(f"   • Font weights found: {len(self.font_weights)}")
        print(f"   • Font families found: {len(self.font_families)}")
        print(f"   • CSS classes found: {len(self.css_classes)}")
        print(f"   • Inline styles found: {len(self.inline_styles)}")
        print(f"   • Chart heights found: {len(self.chart_heights)}")
        print(f"   • Chart color schemes: {len(self.chart_colors)}")
        print(f"   • Chart templates: {len(self.chart_templates)}")
        print(f"   • Table font configs: {len(self.table_fonts)}")
        print(f"   • Key metric styles: {len(self.metric_styles)}")
        print(f"   • Card component styles: {len(self.card_styles)}")
        print(f"   • Filter widget styles: {len(self.filter_styles)}")
        print(f"   • RAG color schemes: {len(self.rag_colors)}")
        print(f"   • RAG status styles: {len(self.rag_styles)}")
        print(f"   • Button styles: {len(self.button_styles)}")
        print(f"   • Badge styles: {len(self.badge_styles)}")
        print(f"   • Icon styles: {len(self.icon_styles)}")
        print(f"   • Alert styles: {len(self.alert_styles)}")
        print(f"   • Layout styles: {len(self.layout_styles)}")
        print(f"   • Spacing styles: {len(self.spacing_styles)}")
        print(f"   • Border styles: {len(self.border_styles)}")
        print(f"   • Animation styles: {len(self.animation_styles)}")
        print(f"   • Tooltip styles: {len(self.tooltip_styles)}")
        print(f"   • Progress styles: {len(self.progress_styles)}")
        print(f"   • Tab styles: {len(self.tab_styles)}")
        print(f"   • Sidebar styles: {len(self.sidebar_styles)}")
        
        # Calculate total disasters
        total_issues = sum(len(issues) for issues in self.issues.values())
        total_chart_issues = sum(len(issues) for issues in self.chart_issues.values())
        total_table_issues = sum(len(issues) for issues in self.table_issues.values())
        total_metric_issues = sum(len(issues) for issues in self.metric_issues.values())
        total_card_issues = sum(len(issues) for issues in self.card_issues.values())
        total_filter_issues = sum(len(issues) for issues in self.filter_issues.values())
        total_rag_issues = sum(len(issues) for issues in self.rag_issues.values())
        total_button_issues = sum(len(issues) for issues in self.button_issues.values())
        total_badge_issues = sum(len(issues) for issues in self.badge_issues.values())
        total_icon_issues = sum(len(issues) for issues in self.icon_issues.values())
        total_alert_issues = sum(len(issues) for issues in self.alert_issues.values())
        total_layout_issues = sum(len(issues) for issues in self.layout_issues.values())
        total_spacing_issues = sum(len(issues) for issues in self.spacing_issues.values())
        total_border_issues = sum(len(issues) for issues in self.border_issues.values())
        total_animation_issues = sum(len(issues) for issues in self.animation_issues.values())
        total_tooltip_issues = sum(len(issues) for issues in self.tooltip_issues.values())
        total_progress_issues = sum(len(issues) for issues in self.progress_issues.values())
        total_tab_issues = sum(len(issues) for issues in self.tab_issues.values())
        total_sidebar_issues = sum(len(issues) for issues in self.sidebar_issues.values())
        
        total_disasters = (total_issues + total_chart_issues + total_table_issues + 
                          total_metric_issues + total_card_issues + total_filter_issues + 
                          total_rag_issues + total_button_issues + total_badge_issues +
                          total_icon_issues + total_alert_issues + total_layout_issues +
                          total_spacing_issues + total_border_issues + total_animation_issues +
                          total_tooltip_issues + total_progress_issues + total_tab_issues +
                          total_sidebar_issues + len(self.inline_styles))
        
        print(f"\n💣 FINAL DISASTER LEVEL: UNIVERSAL APOCALYPSE")
        print(f"   Total styling violations: {total_disasters}")
        print(f"   This exceeds the theoretical maximum for styling disasters.")
        print(f"   The dashboard has achieved impossible levels of inconsistency.")
        print(f"   Emergency evacuation of all styling systems required immediately.")
        print(f"   This is no longer a dashboard - it's a styling crime scene.")

def main():
    auditor = DashboardStyleAuditor()
    auditor.audit_all_pages()

if __name__ == "__main__":
    main() 