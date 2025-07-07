import React, { useState } from 'react'

export interface Tab {
  label: string
  content: React.ReactNode
}

export interface TabNavigationProps {
  tabs: Tab[]
}

export function TabNavigation({ tabs }: TabNavigationProps) {
  const [active, setActive] = useState(0)
  const Active = tabs[active]
  return (
    <div className="tab-navigation">
      <div className="tab-navigation__tabs">
        {tabs.map((t, idx) => (
          <button key={idx} onClick={() => setActive(idx)} className={active === idx ? 'active' : ''}>
            {t.label}
          </button>
        ))}
      </div>
      <div className="tab-navigation__content">{Active.content}</div>
    </div>
  )
}

export default TabNavigation
