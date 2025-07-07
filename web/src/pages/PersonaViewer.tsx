import React from 'react';

const persona = {
  name: 'Marketing Manager',
  goals: 'Increase brand awareness',
  painPoints: 'Limited budget',
};

function PersonaViewer() {
  return (
    <div>
      <h2>Persona Viewer</h2>
      <p>
        <strong>Name:</strong> {persona.name}
      </p>
      <p>
        <strong>Goals:</strong> {persona.goals}
      </p>
      <p>
        <strong>Pain Points:</strong> {persona.painPoints}
      </p>
    </div>
  );
}

export default PersonaViewer;
