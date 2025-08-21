/*
Objective: To test whether the application correctly issues errors when the user enters incorrect or invalid data.

Tests:
     Does an error message appear when an invalid email address is entered?
     Does a warning appear when a blank form is submitted?
     Are errors from the backend (e.g., API failures) correctly reported to the user?

Note: This test checks the application's error management and user notification mechanisms.
*/

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
