import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import type { ListingInfo, ListingParams, OfferParams } from '../../src/types/index.js';

// ==================== TEST CONSTANTS ====================

const MARKETPLACE_ADDRESS = '0x1234567890abcdef1234567890abcdef12345678';
const NFT_CONTRACT = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd';
const SELLER_ADDRESS = '0x1111111111111111111111111111111111111111';
const BUYER_ADDRESS = '0x2222222222222222222222222222222222222222';
const TOKEN_ID = '0x' + '0'.repeat(63) + '1';
const TOKEN_ID_2 = '0x' + '0'.repeat(63) + '2';

// ==================== MOCK HELPERS ====================

function makeMockListing(overrides: Partial<ListingInfo> = {}): ListingInfo {
  return {
    listingId: 1n,
    seller: SELLER_ADDRESS,
    nftContract: NFT_CONTRACT,
    tokenId: TOKEN_ID,
    price: 1000000000000000000n, // 1 LYX
    startTime: Math.floor(Date.now() / 1000) - 3600,
    endTime: Math.floor(Date.now() / 1000) + 86400,
    isActive: true,
    ...overrides,
  };
}

function createMockContractResult(listing: Partial<ListingInfo> = {}) {
  const l = makeMockListing(listing);
  return {
    seller: l.seller,
    nftContract: l.nftContract,
    tokenId: l.tokenId,
    price: l.price,
    startTime: BigInt(l.startTime),
    endTime: BigInt(l.endTime),
    isActive: l.isActive,
  };
}

function createMockOfferResult(overrides: Record<string, unknown> = {}) {
  return {
    buyer: BUYER_ADDRESS,
    nftContract: NFT_CONTRACT,
    tokenId: TOKEN_ID,
    price: 500000000000000000n,
    expiration: BigInt(Math.floor(Date.now() / 1000) + 86400),
    ...overrides,
  };
}

// Use vi.hoisted so these fns are available when vi.mock (which is hoisted) runs
const {
  mockGetListing,
  mockGetListingsByCollection,
  mockGetListingsBySeller,
  mockGetOffer,
  mockGetOffersForToken,
  mockMarketplaceFee,
} = vi.hoisted(() => ({
  mockGetListing: vi.fn(),
  mockGetListingsByCollection: vi.fn(),
  mockGetListingsBySeller: vi.fn(),
  mockGetOffer: vi.fn(),
  mockGetOffersForToken: vi.fn(),
  mockMarketplaceFee: vi.fn(),
}));

// Mock ethers Contract - the mock instance is shared via the hoisted fns
vi.mock('ethers', async () => {
  const actual = await vi.importActual<typeof import('ethers')>('ethers');

  const mockContract = vi.fn().mockImplementation(() => ({
    getListing: mockGetListing,
    getListingsByCollection: mockGetListingsByCollection,
    getListingsBySeller: mockGetListingsBySeller,
    getOffer: mockGetOffer,
    getOffersForToken: mockGetOffersForToken,
    marketplaceFee: mockMarketplaceFee,
  }));

  return {
    ...actual,
    Contract: mockContract,
    ethers: {
      ...actual.ethers,
      Contract: mockContract,
    },
  };
});

// Import after mock setup
import {
  getListing,
  getCollectionListings,
  getSellerListings,
  getCollectionFloorPrice,
  isNFTListed,
  getOffer,
  getOffersForNFT,
  getMarketplaceFee,
  calculateTotalCost,
  encodeCreateListing,
  encodeCancelListing,
  encodeUpdateListingPrice,
  encodeBuyListing,
  encodeMakeOffer,
  encodeAcceptOffer,
  encodeCancelOffer,
  getListingOperations,
  sortListingsByPrice,
  filterActiveListings,
} from '../../src/lib/marketplace.js';

// ==================== ENCODING FUNCTIONS ====================

describe('encodeCreateListing', () => {
  const params: ListingParams = {
    nftContract: NFT_CONTRACT,
    tokenId: TOKEN_ID,
    price: 1000000000000000000n,
    duration: 86400,
  };

  it('returns an ExecuteParams with operationType CALL (0)', () => {
    const result = encodeCreateListing(MARKETPLACE_ADDRESS, params);
    expect(result.operationType).toBe(0);
  });

  it('targets the marketplace address', () => {
    const result = encodeCreateListing(MARKETPLACE_ADDRESS, params);
    expect(result.target).toBe(MARKETPLACE_ADDRESS);
  });

  it('has value of 0n', () => {
    const result = encodeCreateListing(MARKETPLACE_ADDRESS, params);
    expect(result.value).toBe(0n);
  });

  it('encodes non-empty calldata', () => {
    const result = encodeCreateListing(MARKETPLACE_ADDRESS, params);
    expect(result.data).toBeTruthy();
    expect(result.data.startsWith('0x')).toBe(true);
    expect(result.data.length).toBeGreaterThan(10);
  });

  it('includes the createListing function selector in the data', () => {
    const result = encodeCreateListing(MARKETPLACE_ADDRESS, params);
    // createListing(address,bytes32,uint256,uint256) selector
    // Verify the data starts with a 4-byte (10 hex char including 0x) function selector
    expect(result.data).toMatch(/^0x[0-9a-f]{8}/i);
  });

  it('returns all expected ExecuteParams properties', () => {
    const result = encodeCreateListing(MARKETPLACE_ADDRESS, params);
    expect(result).toHaveProperty('operationType');
    expect(result).toHaveProperty('target');
    expect(result).toHaveProperty('value');
    expect(result).toHaveProperty('data');
  });

  it('produces different data for different params', () => {
    const params2: ListingParams = {
      nftContract: NFT_CONTRACT,
      tokenId: TOKEN_ID_2,
      price: 2000000000000000000n,
      duration: 43200,
    };
    const result1 = encodeCreateListing(MARKETPLACE_ADDRESS, params);
    const result2 = encodeCreateListing(MARKETPLACE_ADDRESS, params2);
    expect(result1.data).not.toBe(result2.data);
  });
});

describe('encodeCancelListing', () => {
  const listingId = 42n;

  it('returns an ExecuteParams with operationType CALL (0)', () => {
    const result = encodeCancelListing(MARKETPLACE_ADDRESS, listingId);
    expect(result.operationType).toBe(0);
  });

  it('targets the marketplace address', () => {
    const result = encodeCancelListing(MARKETPLACE_ADDRESS, listingId);
    expect(result.target).toBe(MARKETPLACE_ADDRESS);
  });

  it('has value of 0n', () => {
    const result = encodeCancelListing(MARKETPLACE_ADDRESS, listingId);
    expect(result.value).toBe(0n);
  });

  it('encodes non-empty calldata with cancelListing selector', () => {
    const result = encodeCancelListing(MARKETPLACE_ADDRESS, listingId);
    expect(result.data).toBeTruthy();
    expect(result.data.startsWith('0x')).toBe(true);
  });

  it('produces different data for different listing IDs', () => {
    const result1 = encodeCancelListing(MARKETPLACE_ADDRESS, 1n);
    const result2 = encodeCancelListing(MARKETPLACE_ADDRESS, 2n);
    expect(result1.data).not.toBe(result2.data);
  });
});

describe('encodeUpdateListingPrice', () => {
  const listingId = 10n;
  const newPrice = 2000000000000000000n;

  it('returns an ExecuteParams with operationType CALL (0)', () => {
    const result = encodeUpdateListingPrice(MARKETPLACE_ADDRESS, listingId, newPrice);
    expect(result.operationType).toBe(0);
  });

  it('targets the marketplace address', () => {
    const result = encodeUpdateListingPrice(MARKETPLACE_ADDRESS, listingId, newPrice);
    expect(result.target).toBe(MARKETPLACE_ADDRESS);
  });

  it('has value of 0n', () => {
    const result = encodeUpdateListingPrice(MARKETPLACE_ADDRESS, listingId, newPrice);
    expect(result.value).toBe(0n);
  });

  it('encodes non-empty calldata', () => {
    const result = encodeUpdateListingPrice(MARKETPLACE_ADDRESS, listingId, newPrice);
    expect(result.data).toBeTruthy();
    expect(result.data.startsWith('0x')).toBe(true);
    expect(result.data.length).toBeGreaterThan(10);
  });

  it('produces different data for different prices', () => {
    const result1 = encodeUpdateListingPrice(MARKETPLACE_ADDRESS, listingId, 1000n);
    const result2 = encodeUpdateListingPrice(MARKETPLACE_ADDRESS, listingId, 2000n);
    expect(result1.data).not.toBe(result2.data);
  });
});

describe('encodeBuyListing', () => {
  const listingId = 5n;
  const price = 3000000000000000000n;

  it('returns an ExecuteParams with operationType CALL (0)', () => {
    const result = encodeBuyListing(MARKETPLACE_ADDRESS, listingId, price);
    expect(result.operationType).toBe(0);
  });

  it('targets the marketplace address', () => {
    const result = encodeBuyListing(MARKETPLACE_ADDRESS, listingId, price);
    expect(result.target).toBe(MARKETPLACE_ADDRESS);
  });

  it('has value equal to the price', () => {
    const result = encodeBuyListing(MARKETPLACE_ADDRESS, listingId, price);
    expect(result.value).toBe(price);
  });

  it('value matches the exact price argument', () => {
    const customPrice = 999n;
    const result = encodeBuyListing(MARKETPLACE_ADDRESS, listingId, customPrice);
    expect(result.value).toBe(999n);
  });

  it('encodes non-empty calldata with buyListing selector', () => {
    const result = encodeBuyListing(MARKETPLACE_ADDRESS, listingId, price);
    expect(result.data).toBeTruthy();
    expect(result.data.startsWith('0x')).toBe(true);
  });

  it('value is not 0n when price is non-zero', () => {
    const result = encodeBuyListing(MARKETPLACE_ADDRESS, listingId, 1n);
    expect(result.value).not.toBe(0n);
  });
});

describe('encodeMakeOffer', () => {
  const params: OfferParams = {
    nftContract: NFT_CONTRACT,
    tokenId: TOKEN_ID,
    price: 500000000000000000n,
    duration: 43200,
  };

  it('returns an ExecuteParams with operationType CALL (0)', () => {
    const result = encodeMakeOffer(MARKETPLACE_ADDRESS, params);
    expect(result.operationType).toBe(0);
  });

  it('targets the marketplace address', () => {
    const result = encodeMakeOffer(MARKETPLACE_ADDRESS, params);
    expect(result.target).toBe(MARKETPLACE_ADDRESS);
  });

  it('has value equal to params.price (offer value is locked)', () => {
    const result = encodeMakeOffer(MARKETPLACE_ADDRESS, params);
    expect(result.value).toBe(params.price);
  });

  it('value changes with different offer prices', () => {
    const lowOffer = { ...params, price: 100n };
    const highOffer = { ...params, price: 999999n };
    const resultLow = encodeMakeOffer(MARKETPLACE_ADDRESS, lowOffer);
    const resultHigh = encodeMakeOffer(MARKETPLACE_ADDRESS, highOffer);
    expect(resultLow.value).toBe(100n);
    expect(resultHigh.value).toBe(999999n);
  });

  it('encodes non-empty calldata', () => {
    const result = encodeMakeOffer(MARKETPLACE_ADDRESS, params);
    expect(result.data).toBeTruthy();
    expect(result.data.startsWith('0x')).toBe(true);
    expect(result.data.length).toBeGreaterThan(10);
  });
});

describe('encodeAcceptOffer', () => {
  const offerId = 7n;

  it('returns an ExecuteParams with operationType CALL (0)', () => {
    const result = encodeAcceptOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.operationType).toBe(0);
  });

  it('targets the marketplace address', () => {
    const result = encodeAcceptOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.target).toBe(MARKETPLACE_ADDRESS);
  });

  it('has value of 0n', () => {
    const result = encodeAcceptOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.value).toBe(0n);
  });

  it('encodes non-empty calldata', () => {
    const result = encodeAcceptOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.data).toBeTruthy();
    expect(result.data.startsWith('0x')).toBe(true);
  });

  it('produces different data for different offer IDs', () => {
    const result1 = encodeAcceptOffer(MARKETPLACE_ADDRESS, 1n);
    const result2 = encodeAcceptOffer(MARKETPLACE_ADDRESS, 99n);
    expect(result1.data).not.toBe(result2.data);
  });
});

describe('encodeCancelOffer', () => {
  const offerId = 15n;

  it('returns an ExecuteParams with operationType CALL (0)', () => {
    const result = encodeCancelOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.operationType).toBe(0);
  });

  it('targets the marketplace address', () => {
    const result = encodeCancelOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.target).toBe(MARKETPLACE_ADDRESS);
  });

  it('has value of 0n', () => {
    const result = encodeCancelOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.value).toBe(0n);
  });

  it('encodes non-empty calldata', () => {
    const result = encodeCancelOffer(MARKETPLACE_ADDRESS, offerId);
    expect(result.data).toBeTruthy();
    expect(result.data.startsWith('0x')).toBe(true);
  });

  it('produces different data for different offer IDs', () => {
    const result1 = encodeCancelOffer(MARKETPLACE_ADDRESS, 1n);
    const result2 = encodeCancelOffer(MARKETPLACE_ADDRESS, 200n);
    expect(result1.data).not.toBe(result2.data);
  });
});

// ==================== PURE HELPER FUNCTIONS ====================

describe('sortListingsByPrice', () => {
  const listings: ListingInfo[] = [
    makeMockListing({ listingId: 1n, price: 3000n }),
    makeMockListing({ listingId: 2n, price: 1000n }),
    makeMockListing({ listingId: 3n, price: 5000n }),
    makeMockListing({ listingId: 4n, price: 2000n }),
  ];

  it('sorts listings in ascending order by default', () => {
    const sorted = sortListingsByPrice(listings);
    expect(sorted[0].price).toBe(1000n);
    expect(sorted[1].price).toBe(2000n);
    expect(sorted[2].price).toBe(3000n);
    expect(sorted[3].price).toBe(5000n);
  });

  it('sorts listings in ascending order when explicitly specified', () => {
    const sorted = sortListingsByPrice(listings, true);
    expect(sorted[0].price).toBe(1000n);
    expect(sorted[3].price).toBe(5000n);
  });

  it('sorts listings in descending order', () => {
    const sorted = sortListingsByPrice(listings, false);
    expect(sorted[0].price).toBe(5000n);
    expect(sorted[1].price).toBe(3000n);
    expect(sorted[2].price).toBe(2000n);
    expect(sorted[3].price).toBe(1000n);
  });

  it('does not mutate the original array', () => {
    const original = [...listings];
    sortListingsByPrice(listings);
    expect(listings).toEqual(original);
  });

  it('returns a new array', () => {
    const sorted = sortListingsByPrice(listings);
    expect(sorted).not.toBe(listings);
  });

  it('handles an empty array', () => {
    const sorted = sortListingsByPrice([]);
    expect(sorted).toEqual([]);
  });

  it('handles a single-element array', () => {
    const single = [makeMockListing({ price: 42n })];
    const sorted = sortListingsByPrice(single);
    expect(sorted).toHaveLength(1);
    expect(sorted[0].price).toBe(42n);
  });

  it('handles listings with identical prices', () => {
    const same = [
      makeMockListing({ listingId: 1n, price: 100n }),
      makeMockListing({ listingId: 2n, price: 100n }),
    ];
    const sorted = sortListingsByPrice(same);
    expect(sorted).toHaveLength(2);
    expect(sorted[0].price).toBe(100n);
    expect(sorted[1].price).toBe(100n);
  });
});

describe('filterActiveListings', () => {
  const NOW_SECONDS = 1000000;
  const NOW_MS = NOW_SECONDS * 1000;
  let dateNowSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    dateNowSpy = vi.spyOn(Date, 'now').mockReturnValue(NOW_MS);
  });

  afterEach(() => {
    dateNowSpy.mockRestore();
  });

  it('returns listings that are active, started, and not expired', () => {
    const listings: ListingInfo[] = [
      makeMockListing({
        isActive: true,
        startTime: NOW_SECONDS - 100,
        endTime: NOW_SECONDS + 100,
      }),
    ];
    const result = filterActiveListings(listings);
    expect(result).toHaveLength(1);
  });

  it('filters out inactive listings', () => {
    const listings: ListingInfo[] = [
      makeMockListing({
        isActive: false,
        startTime: NOW_SECONDS - 100,
        endTime: NOW_SECONDS + 100,
      }),
    ];
    const result = filterActiveListings(listings);
    expect(result).toHaveLength(0);
  });

  it('filters out listings that have not started yet', () => {
    const listings: ListingInfo[] = [
      makeMockListing({
        isActive: true,
        startTime: NOW_SECONDS + 100, // future start
        endTime: NOW_SECONDS + 200,
      }),
    ];
    const result = filterActiveListings(listings);
    expect(result).toHaveLength(0);
  });

  it('filters out expired listings', () => {
    const listings: ListingInfo[] = [
      makeMockListing({
        isActive: true,
        startTime: NOW_SECONDS - 200,
        endTime: NOW_SECONDS - 100, // already ended
      }),
    ];
    const result = filterActiveListings(listings);
    expect(result).toHaveLength(0);
  });

  it('includes listing where startTime equals now', () => {
    const listings: ListingInfo[] = [
      makeMockListing({
        isActive: true,
        startTime: NOW_SECONDS, // exactly now
        endTime: NOW_SECONDS + 100,
      }),
    ];
    const result = filterActiveListings(listings);
    expect(result).toHaveLength(1);
  });

  it('excludes listing where endTime equals now (endTime must be > now)', () => {
    const listings: ListingInfo[] = [
      makeMockListing({
        isActive: true,
        startTime: NOW_SECONDS - 100,
        endTime: NOW_SECONDS, // exactly now
      }),
    ];
    const result = filterActiveListings(listings);
    expect(result).toHaveLength(0);
  });

  it('filters a mixed list correctly', () => {
    const listings: ListingInfo[] = [
      makeMockListing({
        listingId: 1n,
        isActive: true,
        startTime: NOW_SECONDS - 100,
        endTime: NOW_SECONDS + 100,
      }),
      makeMockListing({
        listingId: 2n,
        isActive: false,
        startTime: NOW_SECONDS - 100,
        endTime: NOW_SECONDS + 100,
      }),
      makeMockListing({
        listingId: 3n,
        isActive: true,
        startTime: NOW_SECONDS + 50,
        endTime: NOW_SECONDS + 200,
      }),
      makeMockListing({
        listingId: 4n,
        isActive: true,
        startTime: NOW_SECONDS - 500,
        endTime: NOW_SECONDS - 1,
      }),
      makeMockListing({
        listingId: 5n,
        isActive: true,
        startTime: NOW_SECONDS - 200,
        endTime: NOW_SECONDS + 999,
      }),
    ];
    const result = filterActiveListings(listings);
    expect(result).toHaveLength(2);
    expect(result.map((l) => l.listingId)).toEqual([1n, 5n]);
  });

  it('returns an empty array when given an empty array', () => {
    const result = filterActiveListings([]);
    expect(result).toEqual([]);
  });
});

// ==================== WORKFLOW HELPERS ====================

describe('getListingOperations', () => {
  const params: ListingParams = {
    nftContract: NFT_CONTRACT,
    tokenId: TOKEN_ID,
    price: 1000000000000000000n,
    duration: 86400,
  };

  it('returns an array of exactly 2 ExecuteParams', () => {
    const ops = getListingOperations(MARKETPLACE_ADDRESS, params);
    expect(ops).toHaveLength(2);
  });

  it('first operation is the authorize operator call', () => {
    const ops = getListingOperations(MARKETPLACE_ADDRESS, params);
    const authorizeOp = ops[0];
    expect(authorizeOp.operationType).toBe(0);
    expect(authorizeOp.target).toBe(NFT_CONTRACT);
    expect(authorizeOp.value).toBe(0n);
    expect(authorizeOp.data).toBeTruthy();
    expect(authorizeOp.data.startsWith('0x')).toBe(true);
  });

  it('second operation is the create listing call', () => {
    const ops = getListingOperations(MARKETPLACE_ADDRESS, params);
    const listingOp = ops[1];
    expect(listingOp.operationType).toBe(0);
    expect(listingOp.target).toBe(MARKETPLACE_ADDRESS);
    expect(listingOp.value).toBe(0n);
    expect(listingOp.data).toBeTruthy();
    expect(listingOp.data.startsWith('0x')).toBe(true);
  });

  it('authorize targets the NFT contract, not the marketplace', () => {
    const ops = getListingOperations(MARKETPLACE_ADDRESS, params);
    expect(ops[0].target).toBe(params.nftContract);
    expect(ops[0].target).not.toBe(MARKETPLACE_ADDRESS);
  });

  it('listing operation targets the marketplace, not the NFT contract', () => {
    const ops = getListingOperations(MARKETPLACE_ADDRESS, params);
    expect(ops[1].target).toBe(MARKETPLACE_ADDRESS);
    expect(ops[1].target).not.toBe(params.nftContract);
  });

  it('both operations have all ExecuteParams properties', () => {
    const ops = getListingOperations(MARKETPLACE_ADDRESS, params);
    for (const op of ops) {
      expect(op).toHaveProperty('operationType');
      expect(op).toHaveProperty('target');
      expect(op).toHaveProperty('value');
      expect(op).toHaveProperty('data');
    }
  });
});

// ==================== QUERY FUNCTIONS (mocked Contract) ====================

describe('getListing', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns a ListingInfo with the correct shape', async () => {
    mockGetListing.mockResolvedValue(createMockContractResult());

    const result = await getListing(MARKETPLACE_ADDRESS, 1n, {} as any);
    expect(result).toHaveProperty('listingId');
    expect(result).toHaveProperty('seller');
    expect(result).toHaveProperty('nftContract');
    expect(result).toHaveProperty('tokenId');
    expect(result).toHaveProperty('price');
    expect(result).toHaveProperty('startTime');
    expect(result).toHaveProperty('endTime');
    expect(result).toHaveProperty('isActive');
  });

  it('passes the listing ID to the contract method', async () => {
    mockGetListing.mockResolvedValue(createMockContractResult());

    await getListing(MARKETPLACE_ADDRESS, 42n, {} as any);
    expect(mockGetListing).toHaveBeenCalledWith(42n);
  });

  it('preserves the listingId in the returned object', async () => {
    mockGetListing.mockResolvedValue(createMockContractResult());

    const result = await getListing(MARKETPLACE_ADDRESS, 99n, {} as any);
    expect(result.listingId).toBe(99n);
  });

  it('converts startTime and endTime to numbers', async () => {
    mockGetListing.mockResolvedValue(
      createMockContractResult({ startTime: 1000, endTime: 2000 })
    );

    const result = await getListing(MARKETPLACE_ADDRESS, 1n, {} as any);
    expect(typeof result.startTime).toBe('number');
    expect(typeof result.endTime).toBe('number');
  });

  it('maps seller, nftContract, tokenId, price, isActive from the contract result', async () => {
    const contractResult = createMockContractResult({
      seller: SELLER_ADDRESS,
      nftContract: NFT_CONTRACT,
      tokenId: TOKEN_ID,
      price: 5000n,
      isActive: true,
    });
    mockGetListing.mockResolvedValue(contractResult);

    const result = await getListing(MARKETPLACE_ADDRESS, 1n, {} as any);
    expect(result.seller).toBe(SELLER_ADDRESS);
    expect(result.nftContract).toBe(NFT_CONTRACT);
    expect(result.tokenId).toBe(TOKEN_ID);
    expect(result.price).toBe(5000n);
    expect(result.isActive).toBe(true);
  });
});

describe('getCollectionListings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns an array of ListingInfo', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n, 2n]);
    mockGetListing
      .mockResolvedValueOnce(createMockContractResult({ isActive: true }))
      .mockResolvedValueOnce(createMockContractResult({ isActive: true }));

    const result = await getCollectionListings(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(Array.isArray(result)).toBe(true);
    expect(result).toHaveLength(2);
  });

  it('only returns active listings', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n, 2n, 3n]);
    mockGetListing
      .mockResolvedValueOnce(createMockContractResult({ isActive: true }))
      .mockResolvedValueOnce(createMockContractResult({ isActive: false }))
      .mockResolvedValueOnce(createMockContractResult({ isActive: true }));

    const result = await getCollectionListings(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(result).toHaveLength(2);
  });

  it('returns empty array when no listings exist', async () => {
    mockGetListingsByCollection.mockResolvedValue([]);

    const result = await getCollectionListings(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(result).toEqual([]);
  });

  it('skips invalid listings without throwing', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n, 2n]);
    mockGetListing
      .mockRejectedValueOnce(new Error('invalid listing'))
      .mockResolvedValueOnce(createMockContractResult({ isActive: true }));

    const result = await getCollectionListings(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(result).toHaveLength(1);
  });

  it('calls getListingsByCollection with the correct nft contract address', async () => {
    mockGetListingsByCollection.mockResolvedValue([]);

    await getCollectionListings(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(mockGetListingsByCollection).toHaveBeenCalledWith(NFT_CONTRACT);
  });
});

describe('getSellerListings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns an array of ListingInfo (including inactive)', async () => {
    mockGetListingsBySeller.mockResolvedValue([1n, 2n]);
    mockGetListing
      .mockResolvedValueOnce(createMockContractResult({ isActive: true }))
      .mockResolvedValueOnce(createMockContractResult({ isActive: false }));

    const result = await getSellerListings(MARKETPLACE_ADDRESS, SELLER_ADDRESS, {} as any);
    // getSellerListings does not filter by isActive
    expect(result).toHaveLength(2);
  });

  it('returns empty array when seller has no listings', async () => {
    mockGetListingsBySeller.mockResolvedValue([]);

    const result = await getSellerListings(MARKETPLACE_ADDRESS, SELLER_ADDRESS, {} as any);
    expect(result).toEqual([]);
  });

  it('calls getListingsBySeller with the correct seller address', async () => {
    mockGetListingsBySeller.mockResolvedValue([]);

    await getSellerListings(MARKETPLACE_ADDRESS, SELLER_ADDRESS, {} as any);
    expect(mockGetListingsBySeller).toHaveBeenCalledWith(SELLER_ADDRESS);
  });

  it('skips invalid listings without throwing', async () => {
    mockGetListingsBySeller.mockResolvedValue([1n, 2n]);
    mockGetListing
      .mockRejectedValueOnce(new Error('bad listing'))
      .mockResolvedValueOnce(createMockContractResult());

    const result = await getSellerListings(MARKETPLACE_ADDRESS, SELLER_ADDRESS, {} as any);
    expect(result).toHaveLength(1);
  });
});

describe('getCollectionFloorPrice', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns the lowest price among active listings', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n, 2n, 3n]);
    mockGetListing
      .mockResolvedValueOnce(createMockContractResult({ isActive: true, price: 3000n }))
      .mockResolvedValueOnce(createMockContractResult({ isActive: true, price: 1000n }))
      .mockResolvedValueOnce(createMockContractResult({ isActive: true, price: 5000n }));

    const result = await getCollectionFloorPrice(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(result).toBe(1000n);
  });

  it('returns null when there are no active listings', async () => {
    mockGetListingsByCollection.mockResolvedValue([]);

    const result = await getCollectionFloorPrice(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(result).toBeNull();
  });

  it('returns null when all listings are inactive', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n, 2n]);
    mockGetListing
      .mockResolvedValueOnce(createMockContractResult({ isActive: false }))
      .mockResolvedValueOnce(createMockContractResult({ isActive: false }));

    const result = await getCollectionFloorPrice(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(result).toBeNull();
  });

  it('returns the single price when only one active listing exists', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n]);
    mockGetListing.mockResolvedValueOnce(
      createMockContractResult({ isActive: true, price: 7777n })
    );

    const result = await getCollectionFloorPrice(MARKETPLACE_ADDRESS, NFT_CONTRACT, {} as any);
    expect(result).toBe(7777n);
  });
});

describe('isNFTListed', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns { listed: true, listingId, price } when NFT is listed', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n]);
    mockGetListing.mockResolvedValueOnce(
      createMockContractResult({
        isActive: true,
        nftContract: NFT_CONTRACT,
        tokenId: TOKEN_ID,
        price: 9999n,
      })
    );

    const result = await isNFTListed(MARKETPLACE_ADDRESS, NFT_CONTRACT, TOKEN_ID, {} as any);
    expect(result.listed).toBe(true);
    expect(result.listingId).toBeDefined();
    expect(result.price).toBe(9999n);
  });

  it('returns { listed: false } when NFT is not listed', async () => {
    mockGetListingsByCollection.mockResolvedValue([1n]);
    mockGetListing.mockResolvedValueOnce(
      createMockContractResult({
        isActive: true,
        nftContract: NFT_CONTRACT,
        tokenId: TOKEN_ID_2, // different token
      })
    );

    const result = await isNFTListed(MARKETPLACE_ADDRESS, NFT_CONTRACT, TOKEN_ID, {} as any);
    expect(result.listed).toBe(false);
    expect(result.listingId).toBeUndefined();
    expect(result.price).toBeUndefined();
  });

  it('returns { listed: false } when no listings exist', async () => {
    mockGetListingsByCollection.mockResolvedValue([]);

    const result = await isNFTListed(MARKETPLACE_ADDRESS, NFT_CONTRACT, TOKEN_ID, {} as any);
    expect(result.listed).toBe(false);
  });

  it('performs case-insensitive comparison on nftContract address', async () => {
    const lowerCaseContract = NFT_CONTRACT.toLowerCase();
    mockGetListingsByCollection.mockResolvedValue([1n]);
    mockGetListing.mockResolvedValueOnce(
      createMockContractResult({
        isActive: true,
        nftContract: lowerCaseContract,
        tokenId: TOKEN_ID,
        price: 42n,
      })
    );

    const result = await isNFTListed(
      MARKETPLACE_ADDRESS,
      NFT_CONTRACT.toUpperCase().replace('0X', '0x'),
      TOKEN_ID,
      {} as any
    );
    expect(result.listed).toBe(true);
  });
});

describe('getOffer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns an OfferInfo with the correct shape', async () => {
    mockGetOffer.mockResolvedValue(createMockOfferResult());

    const result = await getOffer(MARKETPLACE_ADDRESS, 1n, {} as any);
    expect(result).toHaveProperty('offerId');
    expect(result).toHaveProperty('buyer');
    expect(result).toHaveProperty('nftContract');
    expect(result).toHaveProperty('tokenId');
    expect(result).toHaveProperty('price');
    expect(result).toHaveProperty('expiration');
  });

  it('passes the offer ID to the contract method', async () => {
    mockGetOffer.mockResolvedValue(createMockOfferResult());

    await getOffer(MARKETPLACE_ADDRESS, 55n, {} as any);
    expect(mockGetOffer).toHaveBeenCalledWith(55n);
  });

  it('preserves the offerId in the returned object', async () => {
    mockGetOffer.mockResolvedValue(createMockOfferResult());

    const result = await getOffer(MARKETPLACE_ADDRESS, 77n, {} as any);
    expect(result.offerId).toBe(77n);
  });

  it('converts expiration to a number', async () => {
    mockGetOffer.mockResolvedValue(createMockOfferResult({ expiration: 99999n }));

    const result = await getOffer(MARKETPLACE_ADDRESS, 1n, {} as any);
    expect(typeof result.expiration).toBe('number');
    expect(result.expiration).toBe(99999);
  });
});

describe('getOffersForNFT', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns an array of non-expired OfferInfo', async () => {
    const futureExpiration = BigInt(Math.floor(Date.now() / 1000) + 86400);
    mockGetOffersForToken.mockResolvedValue([1n, 2n]);
    mockGetOffer
      .mockResolvedValueOnce(createMockOfferResult({ expiration: futureExpiration }))
      .mockResolvedValueOnce(createMockOfferResult({ expiration: futureExpiration }));

    const result = await getOffersForNFT(
      MARKETPLACE_ADDRESS,
      NFT_CONTRACT,
      TOKEN_ID,
      {} as any
    );
    expect(Array.isArray(result)).toBe(true);
    expect(result).toHaveLength(2);
  });

  it('filters out expired offers', async () => {
    const futureExpiration = BigInt(Math.floor(Date.now() / 1000) + 86400);
    const pastExpiration = BigInt(Math.floor(Date.now() / 1000) - 100);
    mockGetOffersForToken.mockResolvedValue([1n, 2n]);
    mockGetOffer
      .mockResolvedValueOnce(createMockOfferResult({ expiration: futureExpiration }))
      .mockResolvedValueOnce(createMockOfferResult({ expiration: pastExpiration }));

    const result = await getOffersForNFT(
      MARKETPLACE_ADDRESS,
      NFT_CONTRACT,
      TOKEN_ID,
      {} as any
    );
    expect(result).toHaveLength(1);
  });

  it('returns empty array when getOffersForToken throws', async () => {
    mockGetOffersForToken.mockRejectedValue(new Error('not supported'));

    const result = await getOffersForNFT(
      MARKETPLACE_ADDRESS,
      NFT_CONTRACT,
      TOKEN_ID,
      {} as any
    );
    expect(result).toEqual([]);
  });

  it('skips individual invalid offers without throwing', async () => {
    const futureExpiration = BigInt(Math.floor(Date.now() / 1000) + 86400);
    mockGetOffersForToken.mockResolvedValue([1n, 2n]);
    mockGetOffer
      .mockRejectedValueOnce(new Error('invalid'))
      .mockResolvedValueOnce(createMockOfferResult({ expiration: futureExpiration }));

    const result = await getOffersForNFT(
      MARKETPLACE_ADDRESS,
      NFT_CONTRACT,
      TOKEN_ID,
      {} as any
    );
    expect(result).toHaveLength(1);
  });

  it('calls getOffersForToken with the correct nftContract and tokenId', async () => {
    mockGetOffersForToken.mockResolvedValue([]);

    await getOffersForNFT(MARKETPLACE_ADDRESS, NFT_CONTRACT, TOKEN_ID, {} as any);
    expect(mockGetOffersForToken).toHaveBeenCalledWith(NFT_CONTRACT, TOKEN_ID);
  });
});

describe('getMarketplaceFee', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns the fee as a bigint', async () => {
    mockMarketplaceFee.mockResolvedValue(250n);

    const result = await getMarketplaceFee(MARKETPLACE_ADDRESS, {} as any);
    expect(result).toBe(250n);
  });

  it('calls the marketplaceFee method on the contract', async () => {
    mockMarketplaceFee.mockResolvedValue(500n);

    await getMarketplaceFee(MARKETPLACE_ADDRESS, {} as any);
    expect(mockMarketplaceFee).toHaveBeenCalled();
  });
});

describe('calculateTotalCost', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns an object with price, fee, and total', async () => {
    mockMarketplaceFee.mockResolvedValue(250n); // 2.5%

    const price = 10000n;
    const result = await calculateTotalCost(MARKETPLACE_ADDRESS, price, {} as any);
    expect(result).toHaveProperty('price');
    expect(result).toHaveProperty('fee');
    expect(result).toHaveProperty('total');
  });

  it('calculates fee correctly at 2.5% (250 bps)', async () => {
    mockMarketplaceFee.mockResolvedValue(250n);

    const price = 10000n;
    const result = await calculateTotalCost(MARKETPLACE_ADDRESS, price, {} as any);
    // fee = 10000 * 250 / 10000 = 250
    expect(result.fee).toBe(250n);
  });

  it('calculates total as price + fee', async () => {
    mockMarketplaceFee.mockResolvedValue(250n);

    const price = 10000n;
    const result = await calculateTotalCost(MARKETPLACE_ADDRESS, price, {} as any);
    expect(result.total).toBe(result.price + result.fee);
  });

  it('preserves the original price in the result', async () => {
    mockMarketplaceFee.mockResolvedValue(100n);

    const price = 5000n;
    const result = await calculateTotalCost(MARKETPLACE_ADDRESS, price, {} as any);
    expect(result.price).toBe(5000n);
  });

  it('handles zero fee', async () => {
    mockMarketplaceFee.mockResolvedValue(0n);

    const price = 10000n;
    const result = await calculateTotalCost(MARKETPLACE_ADDRESS, price, {} as any);
    expect(result.fee).toBe(0n);
    expect(result.total).toBe(price);
  });

  it('handles zero price', async () => {
    mockMarketplaceFee.mockResolvedValue(250n);

    const result = await calculateTotalCost(MARKETPLACE_ADDRESS, 0n, {} as any);
    expect(result.price).toBe(0n);
    expect(result.fee).toBe(0n);
    expect(result.total).toBe(0n);
  });

  it('calculates correctly with large values (1 LYX at 5% fee)', async () => {
    mockMarketplaceFee.mockResolvedValue(500n); // 5%

    const price = 1000000000000000000n; // 1 LYX in wei
    const result = await calculateTotalCost(MARKETPLACE_ADDRESS, price, {} as any);
    // fee = 1e18 * 500 / 10000 = 5e16
    expect(result.fee).toBe(50000000000000000n);
    expect(result.total).toBe(1050000000000000000n);
  });
});
