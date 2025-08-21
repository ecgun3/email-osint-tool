describe('Hata Yönetimi Testleri', () => {
  it('Boş e-posta ile hata verir', () => {
    cy.visit('https://emailosint.onrender.com');
    cy.get('button[type="submit"]').click();
    cy.contains('E-posta alanı boş olamaz').should('be.visible');
  });

  it('Sunucu hatası mesajını gösterir', () => {
    cy.intercept('POST', '/api/email', { statusCode: 500, body: {} });
    cy.visit('https://emailosint.onrender.com');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('button[type="submit"]').click();
    cy.contains('Sunucu hatası, lütfen tekrar deneyin').should('be.visible');
  });
});
