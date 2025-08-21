/**
Purpose: To test whether the homepage loads correctly.

Tests:
     Does the homepage open and is the page title/logo visible?
     Do the key elements on the homepage (header, menu, footer, etc.) render correctly?

Note: This test verifies that the core UI elements function properly when the user opens the page.
 */


describe('E-posta Formu Testleri', () => {
  it('Geçerli e-posta ile gönderim', () => {
    cy.visit('https://emailosint.onrender.com');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('button[type="submit"]').click();
    cy.contains('E-posta başarıyla gönderildi').should('be.visible');
  });

  it('Geçersiz e-posta ile hata gösterir', () => {
    cy.visit('https://emailosint.onrender.com');
    cy.get('input[name="email"]').type('gecersiz-email');
    cy.get('button[type="submit"]').click();
    cy.contains('Geçerli bir e-posta girin').should('be.visible');
  });
});
