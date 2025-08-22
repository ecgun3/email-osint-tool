describe('Domain OSINT Scanner', () => {
  beforeEach(() => {
    // Intercept API calls
    cy.intercept('POST', '/analyze', { fixture: 'analysis-result.json' }).as('analyzeRequest')
    cy.intercept('GET', '/healthz', { status: 'ok' }).as('healthCheck')
    cy.intercept('GET', '/health', { status: 'ok' }).as('healthRender')
    
    // Visit the application
    cy.visit('/')
  })

  describe('Homepage', () => {
    it('should display the main page correctly', () => {
      // Check main elements
      cy.contains('🔍 Domain OSINT Scanner').should('be.visible')
      cy.contains('Analyze domains for MX records and technology stack').should('be.visible')
      
      // Check form elements
      cy.get('#domain').should('be.visible')
      cy.get('#analyze-btn').should('be.visible')
      cy.get('#view-json-btn').should('be.visible')
      
      // Check feature cards
      cy.contains('MX Records').should('be.visible')
      cy.contains('Tech Stack').should('be.visible')
    })

    it('should show the domain input form in bottom left corner', () => {
      // Check positioning (bottom left)
      cy.get('.card').should('have.css', 'position', 'fixed')
      cy.get('.card').should('have.css', 'bottom', '0px')
      cy.get('.card').should('have.css', 'left', '0px')
      
      // Check width
      cy.get('.card').should('have.css', 'width', '400px')
    })

    it('should display API information', () => {
      cy.contains('API: /analyze?domain=example.com&format=json').should('be.visible')
    })
  })

  describe('Domain Analysis', () => {
    it('should analyze a valid domain successfully', () => {
      const testDomain = 'example.com'
      
      // Enter domain and submit
      cy.analyzeDomain(testDomain)
      
      // Check results page
      cy.checkAnalysisResults(testDomain)
      
      // Check for MX section
      cy.contains('MX Records Analysis').should('be.visible')
      
      // Check for BuiltWith section
      cy.contains('Technology Stack Analysis').should('be.visible')
    })

    it('should handle empty domain input', () => {
      cy.get('#analyze-btn').click()
      cy.checkErrorMessage('Please provide a domain to analyze')
    })

    it('should handle invalid domain format', () => {
      cy.get('#domain').type('invalid-domain')
      cy.get('#analyze-btn').click()
      cy.checkErrorMessage('Invalid domain format')
    })

    it('should validate domain input pattern', () => {
      // Test valid domains
      const validDomains = ['example.com', 'test.co.uk', 'sub.domain.org']
      
      validDomains.forEach(domain => {
        cy.get('#domain').clear().type(domain)
        cy.get('#domain').should('not.have.class', 'is-invalid')
      })
    })

    it('should show loading state during analysis', () => {
      cy.get('#domain').type('example.com')
      cy.get('#analyze-btn').click()
      
      // Check loading state
      cy.get('.btn-loading').should('be.visible')
      cy.get('.btn-text').should('not.be.visible')
    })
  })

  describe('Analysis Results', () => {
    beforeEach(() => {
      // Navigate to results page
      cy.analyzeDomain('example.com')
    })

    it('should display MX records correctly', () => {
      cy.contains('MX Records Analysis').should('be.visible')
      
      // Check for MX table or list
      cy.get('table').should('exist')
      cy.contains('Exchange').should('be.visible')
      cy.contains('Priority').should('be.visible')
    })

    it('should display BuiltWith technology stack', () => {
      cy.contains('Technology Stack Analysis').should('be.visible')
      
      // Check for search functionality
      cy.get('#tech-search').should('be.visible')
      cy.get('#tech-clear').should('be.visible')
    })

    it('should have working search functionality', () => {
      // Test search box
      cy.get('#tech-search').type('WordPress')
      cy.get('.tech-card-wrapper').should('have.length.gt', 0)
      
      // Test clear button
      cy.get('#tech-clear').click()
      cy.get('#tech-search').should('have.value', '')
    })

    it('should show Details toggle for multi-variant technologies', () => {
      // Look for technologies with count > 1
      cy.get('.tech-card-wrapper').each(($card) => {
        const countBadge = $card.find('.badge')
        if (countBadge.length > 0) {
          const count = parseInt(countBadge.text())
          if (count > 1) {
            cy.wrap($card).find('.details-toggle').should('be.visible')
          }
        }
      })
    })

    it('should expand and collapse technology details', () => {
      // Find a technology with Details toggle
      cy.get('.details-toggle').first().click()
      cy.get('.variant-item').should('be.visible')
      
      // Collapse
      cy.get('.details-toggle').first().click()
      cy.get('.variant-item').should('not.be.visible')
    })

    it('should display technology categories and counts', () => {
      cy.get('.tech-card-wrapper').each(($card) => {
        // Check for technology name
        cy.wrap($card).find('h6').should('be.visible')
        
        // Check for count badge if count > 1
        const countBadge = $card.find('.badge')
        if (countBadge.length > 0) {
          cy.wrap($card).find('.badge').should('be.visible')
        }
      })
    })
  })

  describe('Navigation and UI', () => {
    it('should navigate back to home page', () => {
      // Go to results page
      cy.analyzeDomain('example.com')
      
      // Click back button
      cy.contains('← New Analysis').click()
      
      // Should be back on home page
      cy.contains('🔍 Domain OSINT Scanner').should('be.visible')
      cy.get('#domain').should('be.visible')
    })

    it('should have working View JSON button', () => {
      cy.get('#domain').type('example.com')
      cy.get('#view-json-btn').click()
      
      // Should open JSON endpoint in new tab
      cy.url().should('include', '/analyze')
      cy.url().should('include', 'format=json')
    })

    it('should have working Print button', () => {
      // Go to results page
      cy.analyzeDomain('example.com')
      
      // Check print button exists
      cy.contains('Print').should('be.visible')
      cy.get('[onclick="window.print()"]').should('exist')
    })

    it('should display timestamp on results page', () => {
      cy.analyzeDomain('example.com')
      
      // Check for timestamp
      cy.contains('Generated at').should('be.visible')
    })
  })

  describe('Responsive Design', () => {
    it('should work on mobile devices', () => {
      cy.setViewport('mobile')
      
      // Check elements are still visible
      cy.get('#domain').should('be.visible')
      cy.get('#analyze-btn').should('be.visible')
      
      // Check card positioning
      cy.get('.card').should('be.visible')
    })

    it('should work on tablet devices', () => {
      cy.setViewport('tablet')
      
      // Check elements are still visible
      cy.get('#domain').should('be.visible')
      cy.get('#analyze-btn').should('be.visible')
    })

    it('should work on desktop devices', () => {
      cy.setViewport('desktop')
      
      // Check elements are still visible
      cy.get('#domain').should('be.visible')
      cy.get('#analyze-btn').should('be.visible')
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', () => {
      // Intercept with error
      cy.intercept('POST', '/analyze', { statusCode: 500 }).as('analyzeError')
      
      cy.get('#domain').type('example.com')
      cy.get('#analyze-btn').click()
      
      cy.wait('@analyzeError')
      cy.contains('An unexpected error occurred').should('be.visible')
    })

    it('should handle 404 errors', () => {
      cy.visit('/nonexistent')
      cy.contains('404').should('be.visible')
    })
  })

  describe('Performance', () => {
    it('should load page quickly', () => {
      cy.visit('/', { onBeforeLoad: (win) => {
        win.performance.mark('start')
      }})
      
      cy.get('#domain').should('be.visible').then(() => {
        cy.window().then((win) => {
          win.performance.mark('end')
          win.performance.measure('pageLoad', 'start', 'end')
          
          const measure = win.performance.getEntriesByName('pageLoad')[0]
          expect(measure.duration).to.be.lessThan(3000) // Less than 3 seconds
        })
      })
    })
  })
})