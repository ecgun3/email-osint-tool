describe('Homepage Testleri', () => {
  it('Ana sayfa yükleniyor', () => {
    cy.visit('https://emailosint.onrender.com');
    cy.contains('Email OSINT').should('be.visible');
    cy.get('input[name="email"]').should('exist');
    cy.get('button[type="submit"]').should('exist');
  });
});
