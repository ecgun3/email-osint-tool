/* 
Purpose: To test whether the homepage loads correctly.

Tests:
     Does the homepage open and is the page title/logo visible?
     Do the key elements on the homepage (header, menu, footer, etc.) render correctly?

Note: This test verifies that the core UI elements function properly when the user opens the page.
*/

describe('Homepage Testleri', () => {
  it('Ana sayfa yükleniyor', () => {
    cy.visit('https://emailosint.onrender.com');
    cy.contains('Email OSINT').should('be.visible');
    cy.get('input[name="email"]').should('exist');
    cy.get('button[type="submit"]').should('exist');
  });
});
