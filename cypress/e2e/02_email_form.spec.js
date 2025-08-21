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
